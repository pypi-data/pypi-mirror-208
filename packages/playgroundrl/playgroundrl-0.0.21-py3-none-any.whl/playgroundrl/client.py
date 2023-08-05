import socketio
from abc import ABC, abstractmethod
import requests
import webbrowser
from urllib.parse import urljoin
from typing import Dict, Union
from enum import Enum
from .state import *
import cattrs
import json

class GameType(Enum):
    """Enumeration of different supported games"""
    SNAKE = 'snake'

    TICTACTOE = 'tic_tac_toe'

    CHESS = 'chess'

    CATAN = 'catan'

    POKER = 'poker'

    GO = 'go'

    CODENAMES = 'codenames'

    MININGDECARBONIZATION = 'mining_decarbonization'

TYPE_MAPPING = {
    GameType.SNAKE : SnakeState,
    GameType.TICTACTOE: TicTacToeState,
    GameType.CHESS: ChessState,
    GameType.CATAN: CatanState,
    GameType.POKER: PokerState,
    GameType.GO: GoState,
    GameType.CODENAMES: CodenamesState,
    GameType.MININGDECARBONIZATION: MiningDecarbonizationState,
}

# Hack to get cattrs to parse catan actions correctl 
def hook(d, t):
    return d

cattrs.register_structure_hook(Union[str, List[str]],  hook )

class Pool(Enum):
    """
    The pool determines the possible agents a user or model 
    can match with during games. 
    """

    HUMAN_ONLY = 0
    """ Humans playing humans (unjoinable by models) """

    MODEL_ONLY = 1
    """Models playing models"""

    OPEN = 2
    """Both humans and models playing each other"""


# TODO: Handle retrying and what happens if we never receive a message back ()
# TODO: Turn print statements into logging statements
# TODO: Turn Dict messages into classes
# TODO: Kill the client better, sometimes it hangs
# TODO: Create enums for game_types (MODEL_ONLY=1, OPEN_POOL=2)
class PlaygroundClient(ABC):
    """
    The base client to interface with the server. Handles all non-game specific logic. 

    See example usage at https://playgroundrl.com/guide. 
    """
    def __init__(
        self,
        game: GameType,
        model_name: str,
        auth: Dict = None,
        auth_file: str = None,
        endpoint: str = "https://cdn.playgroundrl.com:8083",
        render_gameplay: bool = False,
    ):
        """
        Initializes a client Object and connects to the server. 

        :param game: String representing game name. 'tictactoe', 'chess', or 'snake'. 
        :param model_name: Name of your RL model. Should be distinct in your user. 
        :param auth: Dictionary containing auth data. In simple case, should contain 
                'email' and 'api_key' fields.
        :param auth_file: File containing endpoint and authdata (mutually exclusive with `auth and `endpoint`).
                Expects a JSON file, structured as {"endpoint": ..., "auth": {"api_key": ..., "email": ...}}
        :param endpoint: URL of backend endpoint to connect to. Mainly used for
                connecting to development server. 
        :param render_gameplay: Whether to visualize game-play server-side
        """

        # Retrieve user id
        # urljoin has weird behavior when it's not terminated right
        if auth_file is not None:
            with open(auth_file, 'r') as f:
                data = json.loads(f.read())
                endpoint = data["endpoint"]
                auth = data["auth"]
            
        if not endpoint.endswith('/'):
            endpoint += '/'
        
        url = urljoin(endpoint, 'email_to_uid')
        response = requests.get(url, params={"email": auth["email"]})
        assert(response.text != "email not found")
        assert(response.status_code == 200)
        self.user_id = response.text

        print("Connecting....")
        self.sio = socketio.Client()
        socket_auth = {"user_id": self.user_id, "api_key": auth["api_key"], "is_human": False}

        self.sio.connect(endpoint, auth=socket_auth, namespaces=["/"])
        self._register_handlers()
        print("Connected!")

        self.server_side_sid = None
        if render_gameplay:
            self.sio.emit("request_server_side_sid", {})

        self.game_type = game
        self.model_name = model_name
        self.endpoint = endpoint
        self.pool = 1
        self.num_games = 1
        self.game_id = None
        self.self_training = False
        self.maximum_messages = 50000
        self.exchanged = 0

    @abstractmethod
    def callback(self, state: GameState, reward: str) -> str:
        """
        User defined callback to implement RL strategies.

        Returns the action for the client to take,
        or none for no action.
        """
        # TODO: Make self, state, and reward proper objects
        pass

    @abstractmethod
    def gameover_callback(self) -> None:
        """User-defined callback to run an action when the game ends"""
        pass

    def is_current_user_move(self, state: GameState) -> bool:
        """
        Returns whether it is our move 
        """
        _user = state.player_moving
        _model_name = state.model_name
        return self.user_id == _user

    def run(self,
            pool: Pool = Pool(1),
            num_games: int = 1,
            maximum_messages: int = 5000,
            self_training: bool = False,
            game_parameters: Dict = {}
            ) -> None:
        """
        Starts game(s), and runs game(s) until completion. 
        :param pool: Which game pool to play in, must be MODEL_ONLY or OPEN.
        :param num_games: Number of games to play before disconnecting
        :param maximum_messages: A timeout to prevent games from going on forever.
        :param self_training: Perform self-training. Instead of being matched with another
            player, this class will be responsible for all players in the game
        """
        assert(pool.value in [1, 2])
        assert(num_games >= 1)

        self.pool = pool
        self.num_games = num_games
        self.game_id = None
        self.self_training = self_training
        self.maximum_messages = maximum_messages
        self.game_parameters = game_parameters
        self.exchanged = 0

        print("  --running")
        self.num_games -= 1
        self.sio.emit(
            "start_game",
            {
                "game": self.game_type.value,
                "game_type": self.pool.value,
                "model_name": self.model_name,
                "self_training": self.self_training,
                "game_parameters": self.game_parameters,
            },
        )
        self.sio.wait()

    def _register_handlers(self):
        self.sio.on("return_server_side_sid", lambda msg: self._on_get_server_side_sid(msg))
        self.sio.on("state_msg", lambda msg: self._on_state_msg(msg))
        # this now happens by default, when the state updated correctly
        self.sio.on("ack", lambda msg: self._on_action_ack_msg(msg))
        self.sio.on("game_over", lambda msg: self._on_game_over_msg(msg))
        self.sio.on("send_game_id", lambda msg: self._on_send_game_id_msg(msg))
        self.sio.on("exception", lambda msg: self._on_error_msg(msg))
        self.sio.on("*", lambda type, msg: self._default_callback(self, type, msg))

    def _on_get_server_side_sid(self, msg):
        self.server_side_sid = msg["server_side_sid"]

    def _on_state_msg(self, msg):
        print(" --state_msg received: ", msg)
        state = msg["state"]
        reward = msg["reward"]
        is_game_over = msg["is_game_over"]
        if is_game_over or self.exchanged > self.maximum_messages:
            print(
                "Game is over or max number of messages has been reached..."
            )
            self.gameover_callback()
            # self.sio.disconnect()
            return

        # Convert state from JSON to object
        state_type = TYPE_MAPPING[self.game_type]
        # converter = cattrs.Converter(detailed_validation=False)  # turn this off later for faster structure
        state = cattrs.structure(json.loads(state), state_type)

        action = self.callback(state, reward)
        if action is not None:
            payload = {"action": action, "game_id": self.game_id}
            print(" -- sending action: ", action)
            self.sio.emit("submit_agent_action", payload)

        self.exchanged += 1

    def _on_action_ack_msg(self, msg):
        print(" --ack message received", msg)
        # self.sio.emit('get_state', {'game_id': self.game_id})

    # TODO: handle this gracefully
    def _on_game_over_msg(self, msg):
        print(f"  --Game ended. Outcome for player {msg['player_id']}:  {msg['outcome']}")
        if self.num_games <= 0:
            self.sio.disconnect()
            exit()
        self.run()

    def _on_send_game_id_msg(self, msg):
        print("  --send_game_id message received", msg)
        if self.render_gameplay and self.game_id is None and self.server_side_sid is not None:
            # TODO: figure out a cleaner way to do this
            url = self.endpoint.replace(":8083/", "/").replace("stagingcdn", "dev").replace("cdn.", "")
            if ".com" not in url:
                url = url[:-1]
                url += ":3000/"
            webbrowser.open(url
                            + self.game_type.value.replace("_", "")
                            + "/?listen_to_sid="
                            + self.server_side_sid)

        self.game_id = msg["game_id"]
        assert self.game_id is not None

        # Server sends player_ids this client has ownership over 
        self.player_ids = msg['player_ids']

        self.sio.emit("get_state", {"game_id": self.game_id, "player_id": self.player_ids[0]})


    def _default_callback(self, msg_type, msg):
        raise Exception("Received unexpected data from server: " + msg_type + msg)

    def _on_error_msg(self, msg):
        raise Exception(msg)


