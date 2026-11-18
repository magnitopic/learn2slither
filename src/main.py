from core.program_arguments import handleArgs, loadProgramConfig
from ui.Screen import Screen
from aux.enums import Move
from aux.colours import RED, GREEN, YELLOW, CYAN, RESET
import pygame
import yaml
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


def game_loop(board, screen, move):
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
        """ if gameConfig["human_player"]: """
        print(f"{RED}Game Over: {e}{RESET}")
        running = False
        return
        """ else:  # if game ends and it's IA, reset the game
            print(f"{YELLOW}RESET: {e}{RESET}")
            print("-"*20)
            move = None
            board.reset() """

    # Draw everything
    screen.draw_board(board)


def main_loop(board, screen):
    clock = pygame.time.Clock()
    game_speed = 1  # Speed from 1-5
    running = True
    paused = False
    move = None
    step_by_step = False

    # Draw initial board
    # screen.draw_board(board)

    while running:
        # Handle events
        for event in pygame.event.get():
            running, paused, move, game_speed, step_by_step = handleEvents(
                board, event, running, paused, move, game_speed, step_by_step)

        # Run game logic
        if board.show_lobby:
            screen.draw_lobby()
            """ board.show_lobby = False """
        else:
            if not paused or step_by_step:
                game_loop(board, screen, move)
                step_by_step = False

        # FPS
        clock.tick(game_speed * 2)

    pygame.quit()


if __name__ == "__main__":

    program_args, loaded_data, board, screen = loadProgramConfig()

    main_loop(board, screen)

    print(f"{CYAN}✌️ Game finished{RESET}")
