from tqdm import tqdm


class Trainer:
    def __init__(self, board, gameConfig):
        # Global values
        self.sessions = gameConfig['sessions']
        self.max_steps = gameConfig['max_steps']
        self.target_avg_len = gameConfig['target_avg_len']

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
        self.step_by_step = False

    def train(self, board, agent):
        print(f"Starting training for {self.sessions} sessions ⚙️")

        for episode in range(self.sessions):
            self.current_episode += 1

            self.run_episode(board, agent)

        final_stats = self.get_stats()

        return final_stats

    def run_episode(self, board, agent):
        board.reset()
        self.episode_reward = 0
        self.episode_steps = 0
        self.episode_losses = []

        # TODO -> if screen, update with initial state

        while not self.game_over:
            action = agent.select_action(board, training=True)

            try:
                reward, loss = board.handleTurn(action)
            except ValueError as e:
                print(f"{YELLOW}RESET: {e}{RESET}")
                loss = -100 # death penalty
                self.game_over = True

            # update stats
            self.total_steps += 1
            self.episode_steps += 1
            self.episode_losses.append(loss)
            episode_reward += reward

            if self.episode_steps > self.max_steps:
                self.game_over = True
                break

    def get_stats(self):
        avg_length = self.total_steps / \
            self.current_episode if self.current_episode > 0 else 0
        return {
            "episodes": self.current_episode,
            "total_steps": self.total_steps,
            "best_length": self.best_length,
            "best_score": self.best_score,
            "avg_length": avg_length
        }
