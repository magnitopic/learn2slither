from collections import deque, namedtuple
from typing import Dict, List
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random


Experience = namedtuple('Experience',
                        ['state', 'action', 'reward', 'next_state', 'done'])


class ReplayMemory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = deque(maxlen=capacity)

    def push(self, state: np.ndarray, action: int, reward: float,
             next_state: np.ndarray, done: bool):
        self.memory.append(Experience(state, action, reward, next_state, done))

    def sample(self, batch_size: int) -> List[Experience]:
        return random.sample(self.memory, batch_size)

    def __len__(self) -> int:
        return len(self.memory)

    def clear(self):
        self.memory.clear()

    def get_statistics(self) -> Dict:
        if len(self.memory) == 0:
            return {
                'size': 0,
                'capacity': self.capacity,
                'utilization': 0.0
            }

        rewards = [exp.reward for exp in self.memory]
        return {
            'size': len(self.memory),
            'capacity': self.capacity,
            'utilization': len(self.memory) / self.capacity,
            'avg_reward': np.mean(rewards),
            'min_reward': np.min(rewards),
            'max_reward': np.max(rewards)
        }


class DQNAgent:
    def __init__(self, config, device: str = 'cpu'):
        if config['args']["dontlearn"]:
            self.epsilon = 0.0
        else:
            self.epsilon = config['epsilon']

    def select_action(self, board):

        if random.random() > self.epsilon:
            # Use the model to predict the best action
            with torch.no_grad():
                state_tensor = torch.FloatTensor(
                    board.get_state()).unsqueeze(0).to(self.device)
                q_values = self.q_network(state_tensor)
                action = q_values.argmax(1).item()
        else:
            action = random.randint(0, 2)

        return action
