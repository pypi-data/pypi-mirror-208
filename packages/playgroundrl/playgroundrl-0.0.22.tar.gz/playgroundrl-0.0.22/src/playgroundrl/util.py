import sys, json

def read_params_from_file():
    # Quick script to read in params from filename
    if len(sys.argv) < 2:
        print("Pass in file containing endpoint and auth argument")
        sys.exit()

    config_filename = sys.argv[1]
    # Read auth, endpoint from file 
    with open(config_filename, 'r') as f:
        params = json.loads(f.read())
    
        return params

# def read_params_from_cli():