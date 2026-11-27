from aux.colours import RED, RESET
from ui.Screen import Screen
from core.Board import Board
from training.Trainer import Trainer
from agent.Agent import DQNAgent
import yaml
import os
import sys


def handleArgs():
    '''
    Arguments:

    - sessions <int>
    - save <path>
    - load <path>
    - dontlearn
    - visual <on/off>
    - stepbystep
    - config <path>

    ---

    We only show the lobby if visual is on and training
    is disabled (dontlearn is set). If visual is off, we
    don't show the lobby and just run the training.

    '''

    values = {
        "sessions": None,
        "save": None,
        "load": None,
        "dontlearn": False,
        "stepbystep": False,
        "config": "snake.yml",
        "visual": "on",
        "showlobby": False  # derived, not an argument
    }
    with_value = {"sessions", "save", "load", "visual", "config"}
    flags = {"dontlearn", "stepbystep"}

    def fail(message):
        print(f"{RED}Error: {message}{RESET}")
        sys.exit(2)

    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        name = argv[i].lstrip("-").replace("-", "")
        if not argv[i].startswith("-") or name not in with_value | flags:
            fail(f"Unknown argument '{argv[i]}'.")

        if name in flags:
            values[name] = True
            i += 1
            continue

        if i + 1 >= len(argv) or argv[i + 1].startswith("-"):
            fail(f"Missing value for argument '{argv[i]}'.")
        values[name] = argv[i + 1]
        i += 2

    if values["sessions"] is not None:
        try:
            values["sessions"] = int(values["sessions"])
        except ValueError:
            fail("'-sessions' must be an integer.")
        if values["sessions"] < 1:
            fail("'-sessions' must be at least 1.")

    if values["visual"] not in ("on", "off"):
        fail("'-visual' must be 'on' or 'off'.")

    for key in ("load", "config"):
        if values[key] is not None and not os.path.isfile(values[key]):
            fail(f"File '{values[key]}' (-{key}) does not exist.")

    # Argument combinations that make no sense
    if values["dontlearn"] and values["load"] is None:
        fail("'-dontlearn' needs a model to run. Use -load <path>.")
    if values["stepbystep"] and values["visual"] == "off":
        fail("'-stepbystep' needs the display. Use -visual on.")
    if (values["visual"] == "off" and not values["dontlearn"]
            and values["save"] is None):
        fail("Training without display and without '-save' would discard "
             "the result. Use -save <path>.")

    # Lobby only with the display on and when not training
    values["showlobby"] = values["visual"] == "on" and values["dontlearn"]

    return values


def getAllConfigs():
    configs = {}

    # get cmd arguments
    program_args = handleArgs()
    configs["args"] = program_args

    # get yml file arguments
    with open(configs["args"]["config"], 'r') as file:
        loaded_data = yaml.safe_load(file)

    # merge configs onto one dictionary
    configs = configs | loaded_data

    return configs


def loadProgramConfig():
    # Get arguments
    program_configs = getAllConfigs()

    """ try: """
    board: Board = Board(
        program_configs
    )

    # No window when the display is off
    if program_configs["args"]["visual"] == "on":
        screen = Screen(program_configs["game"]["screen"])
    else:
        screen: Screen = None

    agent: DQNAgent = DQNAgent(
        program_configs,
        device='cpu'  # todo -> revise if necessary
    )
    trainer: Trainer = Trainer(
        board,
        program_configs["ai"]["training"],
        screen
    )
    """ except Exception as e:
        print(f"{RED}Error: {e}{RESET}")
        sys.exit(3) """

    return board, screen, trainer, agent
