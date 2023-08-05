import attrs 
from typing import List, Dict
"""
Module with various game state representations
"""

@attrs.define
class GameState():
    player_moving: str
    """user_id of player who's current turn it is"""

    model_name: str
    """name of model who's turn it is next"""

    player_moving_id: int
    """Player id of the player / model who's turn it is next"""

@attrs.define
class ChessState(GameState):
    fen: str 
    """FEN representation of current board state"""


@attrs.define
class SnakeState(GameState):
    apple: List[int]
    """(x, y) of apple"""

    snake: List[List[int]]
    """[(x1, y1), (x2, y2), ... of snake's coordinates]"""


@attrs.define
class MiningDecarbonizationState(GameState):
    mined_resources: List[List[float]]
    """2D array with values from 0 to 1 indicating the resources mined in the last turn for each tile"""

    emissions: List[List[float]]
    """2D array with values from 0 to 1 indicating the emissions produced in the last turn for each tile"""

@attrs.define
class TicTacToeState(GameState):
    board: List[List[int]]
    """Current tic tac toe board"""

    # player_id: int


@attrs.define
class CatanState(GameState):
    tiles: Dict[str, Dict[str, str]]
    """first level keys are tile ids 1... 18.
        second level keys are "resource" with values SHEEP, BRICK, etc
        and "number" with dice sum values 2, 3 etc.
    """

    nodes: Dict[str, Dict[str, str]]
    """first level keys are node ids of the format x_y_z indicating up to
        three tiles that meet at a vertex where the node is.
        second level keys are "building" with values CITY or SETTLEMENT
        and "color" denoting the player color who owns that node
    """

    edges: Dict[str, Dict[str, str]]
    """first level keys are edge ids of the format [node_id]_[node_id]
        to uniquely identify the endpoints of the edge.
        second level keys are "color" with values denoting the player who owns the road
    """

    player_state: Dict[str, str]
    """a variety of properties about the player's state including WOOD_IN_HAND,
        HAS_ROAD, VICTORY_POINTS_IN_HAND, etc.
    """

    colors: List[str]
    """list of all player colors in the game"""

    is_initial_build_phase: bool
    """whether or not in the initial phase of placing first buildings and settlements"""

    robber_coordinate: int
    """tile with the robber"""

    current_prompt: str
    """prompt for the player's action"""

    playable_actions: List[Dict[str, str | List[str]]]
    """all possible actions for the player"""

    longest_roads_by_player: Dict[str, int]
    """length of the longest roads for each player"""

    winning_color: str
    """null if the game is not over, or a player color if someone has won"""

# Card is represented as suit (s, c, h, d)
# concatenated with two 
# digit rank (2 - 14)
Card = str
PokerHand = List[Card]
PlayerId = int


@attrs.define
class RoundOutcome():
    hands: Dict[PlayerId, PokerHand]
    """Mapping of player id to hand in last round"""

    winnings: Dict[PlayerId, int]
    """Mapping of player id to total amount won in last round"""

@attrs.define
class PokerState(GameState):

    communal_cards: List[Card]
    """Board cards"""

    chip_counts = Dict[PlayerId, int]
    """Chip counts for all players"""

    amounts_bet = Dict[PlayerId, int]
    """Amount the player has bet for current round of betting"""

    user_ids = Dict[PlayerId, str]
    """User IDs of each player, useful for utility printing"""
    
    can_raise: bool
    """In certain unique situations, raising is disabled"""

    hand_number: int
    """Which hand we're on (starts at 0, strictly increases)"""

    players_left_in_hand: int
    """How many players that have not folded"""

    status: str
    """(player specific) -- status of current player (IN, OUT, TO_CALL, ALL_IN, )"""


    pot_size: str
    """(player specific) Size of the pot this player is eligible for (always the global pot, 
        except in certain all-in cases)"""


    chips_to_call: int
    """How many chips the player needs to put in to call the next bet (only applicable of state is TO_CALL)"""

    hole_cards: PokerHand
    """Player's secret cards"""

    position: int
    """Position in the round"""

    last_round_state: RoundOutcome | None = None
    """Outcome of last round"""


@attrs.define
class GoState(GameState):
    board: List[List[int]]
    """Board array, -1 is empty, otherwise player id"""

    invalid_moves: List[List[int]]
    """1 if move is invalid (occupied, or ko protection) 0 otherwise"""

    last_move_was_pass: bool
    """Indicator for if last move was pass or not (and thus an additional pass ends the game)"""


@attrs.define
class CodenamesState(GameState):
    color: str
    """Color of player receiving state"""

    role: str
    """Role of player receiving state (giver / guesser)"""

    words: List[List[str]]
    """
    5x5 array of words representing board
    """

    guessed: List[List[str]]
    """
    Colors revealed already through guesses.
    BLUE / RED / INNOCENT / ASSASSIN / UNKNOWN
    """

    actual: List[List[str]]
    """
    For giver, the actual values for each tile
    For guesser, the same as guessed. 
    """

    clue: str
    """
    Most recently given clue (one word)
    """
    
    count: int
    """
    Count for most recent clue
    """

    scores: Dict[str, int]
    """
    Color to score mapping
    """