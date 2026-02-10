from classes.Board import Board
from classes.Screen import Screen
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


def main_loop(board, screen):
    clock = pygame.time.Clock()
    game_speed = 3  # Speed from 1-5
    running = True
    paused = False

    number_keys = ["K_1", "K_2", "K_3", "K_4", "K_5"]

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

        # Run game logic
        if not paused:
            screen.print_board(board)

        # FPS
        clock.tick(game_speed * 5)

    pygame.quit()


if __name__ == "__main__":
    # Get arguments
    program_args = handleArgs()

    # Get data from yaml file
    with open('snake.yml', 'r') as file:
        loaded_data = yaml.safe_load(file)

    board: Board = Board(loaded_data["game"]["board"])
    screen: Screen = Screen(loaded_data["game"]["screen"])

    main_loop(board, screen)

    print(f"{CYAN}✌️ Game finished{RESET}")
