
class Trainer:
    def __init__(self, board, gameConfig):
        # Global values
        self.episodes = gameConfig['episodes']
        self.max_steps = gameConfig['max_steps']
        self.target_avg_len = gameConfig['target_avg_len']

        # Current training state
        self.current_episode = 0
        self.total_steps = 0
        self.best_length = 0
        self.best_score = 0
        self.step_by_step = False

    def train(self, num_sessions: int):
        print(f"Starting training for {num_sessions} episodes ⚙️")

