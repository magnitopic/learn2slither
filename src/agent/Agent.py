from collections import deque, namedtuple
from typing import Dict, List
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random

from agent.Model import DQN
from aux.colours import GREEN, RESET


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
        agent_config = config['ai']['agent']
        model_config = config['ai']['model']

        # Hyperparameters from config
        self.device = device
        self.learning_rate = agent_config['learning_rate']
        self.gamma = agent_config['gamma']
        self.epsilon_end = agent_config['epsilon_end']
        self.epsilon_decay = agent_config['epsilon_decay']
        self.batch_size = agent_config['batch_size']
        self.memory_size = agent_config['memory_size']
        self.target_update_freq = agent_config['target_update_frequency']
        self.gradient_clip = agent_config.get('gradient_clip', 0.0)
        self.use_double_dqn = agent_config.get('use_double_dqn', False)
        if config['args']["dontlearn"]:
            self.epsilon = 0.0
        else:
            self.epsilon = agent_config['epsilon_start']

        # Initialize neural networks
        self.q_network = DQN(model_config).to(self.device)
        self.target_network = DQN(model_config).to(self.device)

        # Synchronize target network with Q-network
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()

        # Optimizer
        optimizer_type = agent_config['optimizer'].lower()
        if optimizer_type == 'adam':
            self.optimizer = optim.Adam(
                self.q_network.parameters(), lr=self.learning_rate)
        elif optimizer_type == 'rmsprop':
            self.optimizer = optim.RMSprop(self.q_network.parameters(),
                                           lr=self.learning_rate)
        elif optimizer_type == 'sgd':
            self.optimizer = optim.SGD(
                self.q_network.parameters(), lr=self.learning_rate)
        else:
            raise ValueError(
                f"Unsupported optimizer type: {optimizer_type}. "
                "Supported types are 'adam', 'rmsprop', and 'sgd'.")

        # Loss function
        self.criterion = nn.MSELoss()

        # Memory
        self.memory = ReplayMemory(self.memory_size)

        # Statistics
        self.steps_done = 0
        self.episodes_done = 0
        self.update_counter = 0
        self.learning_enabled = True

        # Training history
        self.loss_history = deque(maxlen=1000)
        self.reward_history = deque(maxlen=1000)
        self.epsilon_history = deque(maxlen=1000)

        print("- Starting DQN Agent -")

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

    def store_experience(self, state, action, reward, next_state, done):
        self.memory.push(state, action, reward, next_state, done)

    def train_step(self):
        if len(self.memory) < self.batch_size or not self.learning_enabled:
            return None

        # Sample a batch of experiences
        experiences = self.memory.sample(self.batch_size)

        # Split batch components
        batch = Experience(*zip(*experiences))

        states = np.array(batch.state, dtype=np.float32)
        actions = np.array(batch.action, dtype=np.int64)
        rewards = np.array(batch.reward, dtype=np.float32)
        next_states = np.array(batch.next_state, dtype=np.float32)
        dones = np.array(batch.done, dtype=np.float32)

        # Convert to tensors
        state_batch = torch.FloatTensor(states).to(self.device)
        action_batch = torch.LongTensor(actions).to(self.device)
        reward_batch = torch.FloatTensor(rewards).to(self.device)
        next_state_batch = torch.FloatTensor(next_states).to(self.device)
        done_batch = torch.FloatTensor(dones).to(self.device)

        # Compute Q values for current states
        current_q_values = self.q_network(
            state_batch).gather(1, action_batch.unsqueeze(1))

        # Compute Q values for next states
        with torch.no_grad():
            if self.use_double_dqn:
                # Double DQN: Use the main network to select the best action
                next_actions = self.q_network(
                    next_state_batch).argmax(1, keepdim=True)
                next_q_values = self.target_network(
                    next_state_batch).gather(1, next_actions)
            else:
                # Standard DQN: Use the target network to get the max Q value
                next_q_values = self.target_network(
                    next_state_batch).max(1)[0].unsqueeze(1)

            # Compute targets with the Bellman equation
            target_q_values = reward_batch.unsqueeze(
                1) + (self.gamma * next_q_values * (1 - done_batch.unsqueeze(1)))

        # compute loss
        loss = self.criterion(current_q_values, target_q_values)

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()

        # gradient clipping to prevent exploding gradients
        if self.gradient_clip > 0:
            nn.utils.clip_grad_norm_(self.q_network.parameters(),
                                     self.gradient_clip)

        self.optimizer.step()

        # register loss
        self.loss_history.append(loss.item())

        self.update_counter += 1

        # update target network if applicable
        if self.update_counter % self.target_update_freq == 0:
            self.update_target_network()

        return loss.item()

    def update_target_network(self):
        self.target_network.load_state_dict(self.q_network.state_dict())
        print(f"{GREEN}Target network updated{RESET}")

    def update_epsilon(self):
        if self.learning_enabled:
            self.epsilon = max(
                self.epsilon_end, self.epsilon * self.epsilon_decay)
            self.epsilon_history.append(self.epsilon)
