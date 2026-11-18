from core.Board import Board
from ui.Screen import Screen
from aux.enums import Move
from aux.colours import RED, GREEN, YELLOW, CYAN, RESET
import pygame
import yaml
import os
import sys

number_keys = ["K_1", "K_2", "K_3", "K_4", "K_5"]
opposite_pairs = {('up', 'down'), ('down', 'up'),
                  ('left', 'right'), ('right', 'left')}
movement_keys = {
    pygame.K_UP: Move.UP,
    pygame.K_DOWN: Move.DOWN,
    pygame.K_LEFT: Move.LEFT,
    pygame.K_RIGHT: Move.RIGHT
}


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
    '''

    values = {
        "sessions": None,
        "save": None,
        "load": None,
        "dontlearn": False,
        "stepbystep": False,
        "config": "snake.yml",
        "visual": "on"
    }
    with_value = {"sessions", "save", "load", "visual", "config"}
    flags = {"dontlearn", "stepbystep"}

    def fail(message):
        print(f"{RED}Error: {message}{RESET}")
        sys.exit(1)

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

    return values


def handleEvents(
        board, event, running, paused, move, game_speed, step_by_step):

    if event.type == pygame.QUIT:
        running = False
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            paused = not paused
            if paused:
                print(f"{YELLOW}⏸️ Game paused{RESET}")
            else:
                print(f"{GREEN}▶️ Game resumed{RESET}")
        elif event.key == pygame.K_d:
            step_by_step = True
        elif event.key == pygame.K_ESCAPE:
            running = False
        elif event.key in [getattr(pygame, key) for key in number_keys]:
            game_speed = int(event.unicode)
            print(f"{YELLOW}⚡ Game speed set to {game_speed}{RESET}")
        elif event.key in movement_keys:
            if (board.snake.current_direction.value,
                    movement_keys[event.key].value) not in opposite_pairs:
                move = movement_keys[event.key]

    return running, paused, move, game_speed, step_by_step


def main_loop(board, screen, gameConfig):
    clock = pygame.time.Clock()
    game_speed = 1  # Speed from 1-5
    running = True
    paused = False
    move = None
    step_by_step = False

    screen.print_board(board)

    while running:
        # Handle events
        for event in pygame.event.get():
            running, paused, move, game_speed, step_by_step = handleEvents(
                board, event, running, paused, move, game_speed, step_by_step)

        # Run game logic
        if not paused or step_by_step:
            if board.snake.show_vision:
                print(board.snakeVision())
                print(board.snake.current_direction)
                print("_"*20)

            # Get snake move
            """ if not gameConfig["human_player"]:
                move = board.snake.move() """

            # Update board state
            try:
                board.handleTurn(move)
            except ValueError as e:
                # if game ends and it's a human player, end the game
                if gameConfig["human_player"]:
                    print(f"{RED}Game Over: {e}{RESET}")
                    running = False
                    continue
                else:  # if game ends and it's IA, reset the game
                    print(f"{YELLOW}RESET: {e}{RESET}")
                    print("-"*20)
                    move = None
                    board.reset()

            # Draw everything
            screen.print_board(board)

            step_by_step = False

        # FPS
        clock.tick(game_speed * 2)

    pygame.quit()


if __name__ == "__main__":
    # Get arguments
    program_args = handleArgs()

    # Get data from yaml file
    with open('snake.yml', 'r') as file:
        loaded_data = yaml.safe_load(file)

    try:
        board: Board = Board(
            loaded_data["game"]["board"], loaded_data["game"]["snake"])
        screen: Screen = Screen(loaded_data["game"]["screen"])
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")
        sys.exit(1)

    main_loop(board, screen, gameConfig=loaded_data["game"])

    print(f"{CYAN}✌️ Game finished{RESET}")
