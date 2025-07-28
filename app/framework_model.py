'''This file defines the FrameworkModel class 
and a function to retrieve the model based on the board name.'''

import sys

class FrameworkModel:
    '''Data class for Framework model info'''

    def __init__(self, board_name, name, image=None, ports=0, overlay_id=0, cpu=None):
        self.board_name = board_name
        self.name = name
        self.image = image
        self.ports = ports
        self.overlay_id = overlay_id
        self.cpu = cpu

def get_framework_model():
    '''Retrieve the Framework model based on the board name from system files'''

    try:
        with open("/sys/class/dmi/id/board_name", encoding="utf-8") as f:
            board = f.read().strip()
    except (FileNotFoundError, OSError):
        board = None

    models = {
        "FRANBMCP03": FrameworkModel(
            board_name="FRANBMCP03",
            name="Framework Laptop 13 (2021)", #11th gen
            image="framework-laptop-13.png",
            ports=4,
            overlay_id="13",
            cpu="Intel Core i5-1135G7"
        ),
        # Add more mappings as needed
    }
    if board in models:
        return models[board]

    # Return an error
    print(f"Warning: Unknown board name '{board}'", file=sys.stderr)

    # Return a default model with the board name
    return FrameworkModel(board_name=board, name=f"Unknown ({board})", image=None, ports=0)
