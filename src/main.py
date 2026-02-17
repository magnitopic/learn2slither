from classes.Board import Board
from classes.Screen import Screen
from enums import Move
from aux.colours import *
import pygame
import yaml
import sys


def handleArgs():
    mode_found = False
    values = {
        "sessions": 0,
        "path": "",
        "mode": "",
        "visual": "on"
    }
    args = list(zip(sys.argv[1::2], sys.argv[2::2]))

    try:
        for arg in args:
            if arg[0] == "-sessions":
                values["sessions"] = int(arg[1])
            elif arg[0] == "-save":
                values["save_path"] = arg[1]
                mode_found = True
            elif arg[0] == "-load":
                values["load_path"] = arg[1]
                mode_found = True
            elif arg[0] == "-visual":
                values["visual"] = arg[1]
                if values["visual"] not in ["on", "off"]:
                    raise ValueError()
    except IndexError:
        print(f"{RED}Error: Missing value for argument.{RESET}")
        sys.exit(1)
    except ValueError:
        print(f"{RED}Error: Invalid value type for argument.{RESET}")
        sys.exit(1)

    if not mode_found:
        print(f"{RED}Error: No mode specified. Use -save or -load.{RESET}")
        sys.exit(1)

    return values


def main_loop(board, screen, gameConfig):
    clock = pygame.time.Clock()
    game_speed = 1  # Speed from 1-5
    running = True
    paused = False
    move = None
    opposite_pairs = {('up', 'down'), ('down', 'up'),
                      ('left', 'right'), ('right', 'left')}

    number_keys = ["K_1", "K_2", "K_3", "K_4", "K_5"]
    movement_keys = {
        pygame.K_UP: Move.UP,
        pygame.K_DOWN: Move.DOWN,
        pygame.K_LEFT: Move.LEFT,
        pygame.K_RIGHT: Move.RIGHT
    }

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                    if paused:
                        print(f"{YELLOW}⏸️ Game paused{RESET}")
                    else:
                        print(f"{GREEN}▶️ Game resumed{RESET}")
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in [getattr(pygame, key) for key in number_keys]:
                    game_speed = int(event.unicode)
                    print(f"{YELLOW}⚡ Game speed set to {game_speed}{RESET}")
                elif event.key in movement_keys:
                    print(board.snake.current_direction.value,
                          movement_keys[event.key].value)
                    if (board.snake.current_direction.value, movement_keys[event.key].value) not in opposite_pairs:
                        move = movement_keys[event.key]

        # Run game logic
        if not paused:
            print(board)
            print("_"*20)

            # Get snake move
            if not gameConfig["human_player"]:
                move = board.snake.move()

            # Update board state
            try:
                board.handleTurn(move)
            except ValueError as e:
                print(f"{RED}Game Over: {e}{RESET}")
                running = False
                continue

            # Draw everything
            screen.print_board(board)

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
