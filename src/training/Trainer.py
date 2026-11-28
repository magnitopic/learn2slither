from aux.colours import YELLOW, RESET
from aux.enums import GameMode
import time


class Trainer:
    def __init__(self, board, gameConfig, screen=None):
        # Global values
        self.sessions = gameConfig['sessions']
        self.max_steps = gameConfig['max_steps']
        self.target_avg_len = gameConfig['target_avg_len']

        # The screen is None when the display is off (-visual off)
        self.screen = screen
        self.step_by_step = board.step_by_step or \
            board.argsConfig["stepbystep"]

        # Session values
        self.episode_reward = 0
        self.episode_steps = 0
        self.episode_losses = []
        self.game_over = False

        # Current training state
        self.current_episode: int = 0
        self.total_steps = 0
        self.best_length = 0
        self.best_score = 0
        self.max_duration = 0
        self.session_max_length = 0
        self.quit = False

    def train(self, board, agent):
        sessions = 1 if board.game_mode == GameMode.HUMAN else self.sessions
        print(f"Starting training for {sessions} sessions ⚙️")

        for episode in range(sessions):
            self.current_episode += 1

            length = self.run_episode(board, agent)

            self.max_duration = max(self.max_duration, self.episode_steps)
            if length > self.session_max_length:
                self.session_max_length = length
                if self.screen:
                    self.screen.update_session_max_length(length)
            if self.screen:
                self.screen.update_previous_episode_length(length)

            if self.quit:
                break

        self.best_length = self.session_max_length
        final_stats = self.get_stats()

        print(f"Game over, max length = {self.best_length}, "
              f"max duration = {self.max_duration}")

        return final_stats

    def run_episode(self, board, agent):
        state = board.reset()
        self.episode_reward = 0
        self.episode_steps = 0
        self.episode_losses = []
        self.game_over = False
        length = board.snake.length

        if self.screen:
            self.screen.move = None
            self.screen.render(board, self.get_display_info(board, agent))
            if self.step_by_step:
                print("🚶 Step by step: SPACE = next turn, ESC = quit")
                if self.screen.wait_for_key_step_by_step(board) == 'quit':
                    self.quit = True
                    return length

        while not self.game_over:
            if self.screen and not self.step_by_step:
                # Normal mode: quit, pause and speed events
                if not self.screen.handle_events(board):
                    self.quit = True
                    break

                while self.screen.paused and not self.screen.step_requested:
                    if not self.screen.handle_events(board):
                        self.quit = True
                        return length
                    time.sleep(0.1)
                self.screen.step_requested = False

            if board.snake.show_vision and self.screen:
                print(board.snakeVision())
                print(board.snake.current_direction)
                print("_"*20)

            # Choose the move: the keyboard or the AI
            if board.game_mode == GameMode.HUMAN:
                action = self.screen.move
            else:
                action = agent.select_action(board)

            # Update board state
            next_state, reward, self.game_over, info = board.handleTurn(action)
            if self.game_over:
                print(f"{YELLOW}RESET{RESET}")
                print("-"*20)

            # Update agent with the new state and reward
            if board.game_mode in [GameMode.AI_TRAIN, GameMode.AI_TEST]:
                agent.store_experience(
                    state, action, reward, next_state, self.game_over)

            state = next_state

            # Train agent
            if board.game_mode == GameMode.AI_TRAIN:
                loss = agent.train_step()
                if loss is not None:
                    self.episode_losses.append(loss)

            # Update stats
            self.total_steps += 1
            self.episode_steps += 1
            if not self.game_over:
                length = max(length, board.snake.length)

            if self.screen and not self.game_over:
                self.screen.render(board, self.get_display_info(board, agent))

                if self.step_by_step:
                    if self.screen.wait_for_key_step_by_step(board) == 'quit':
                        self.quit = True
                        break
                else:
                    self.screen.clock_tick()

            # Limit of steps to avoid infinite loops
            if self.episode_steps >= self.max_steps:
                break

        return length

    def get_display_info(self, board, agent):
        return {
            'episode': self.current_episode,
            'steps': self.episode_steps,
            'length': board.snake.length,
            'epsilon': getattr(agent, 'epsilon', 0),
            'session_max_length': self.session_max_length,
            'step_by_step': self.step_by_step
        }

    def get_stats(self):
        avg_steps = self.total_steps / \
            self.current_episode if self.current_episode > 0 else 0
        return {
            "episodes": self.current_episode,
            "total_steps": self.total_steps,
            "best_length": self.best_length,
            "best_score": self.best_score,
            "avg_steps": avg_steps
        }
