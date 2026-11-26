from core.program_arguments import loadProgramConfig
from aux.colours import RED, YELLOW, CYAN, RESET
from datetime import datetime
import sys


""" def game_loop(board, screen, trainer, move, running):
    if board.snake.show_vision:
        print(board.snakeVision())
        print(board.snake.current_direction)
        print("_"*20)

    # Update board state
    try:
        if board.game_mode in [GameMode.AI_TRAIN, GameMode.AI_TEST]:
            move = trainer.train()
        board.handleTurn(move)
    except ValueError as e:
        # if game ends and it's a human player, end the game
        if board.game_mode == GameMode.HUMAN:
            print(f"{RED}Game Over: {e}{RESET}")
            running = False
            return running, move
        else:  # if game ends and it's IA, reset the game
            print(f"{YELLOW}RESET: {e}{RESET}")
            print("-"*20)
            move = None
            board.reset()

    # Draw everything
    screen.draw_board(board)

    return running, move """


def main_loop(board, screen, trainer, agent):
    try:
        # With the lobby, the game mode is chosen before playing
        if board.show_lobby and not screen.run_lobby(board):
            return

        # Run training
        start_time = datetime.now()
        final_stats = trainer.train(board, agent)
        end_time = datetime.now()

        # print stats
        print(f"Time taken: {end_time - start_time}")
        print("-"*20)
        print(final_stats)
        print("-"*20)

        # TODO -> save model if training

    except KeyboardInterrupt:
        print(f"{YELLOW}Game interrupted by user{RESET}")
        # TODO -> temp
        sys.exit(1)
    except Exception as e:
        print(f"{RED}An error occurred: {e}{RESET}")
        sys.exit(1)
    finally:
        if screen:
            screen.close()


""" def main_loop(board, screen, trainer):
    clock = pygame.time.Clock()
    game_speed = 1  # Speed from 1-5
    running = True
    paused = board.step_by_step
    move = None
    step_by_step = board.step_by_step

    # Draw initial board
    # Todo -> draw starting position
    # screen.draw_board(board)

    while running:
        # Handle events
        for event in pygame.event.get():
            running, paused, move, game_speed, step_by_step = handleEvents(
                board, screen,
                event,
                running,
                paused,
                move,
                game_speed,
                step_by_step
            )

        if board.show_lobby:
            screen.draw_lobby()
        else:
            # Run game logic
            if not paused or step_by_step:
                running, move = game_loop(
                    board, screen, trainer, move, running)
                step_by_step = False

        # FPS
        clock.tick(game_speed * 2)

    pygame.quit() """


if __name__ == "__main__":

    board, screen, trainer, agent = loadProgramConfig()

    main_loop(board, screen, trainer, agent)

    print(f"{CYAN}✌️ Game finished{RESET}")
