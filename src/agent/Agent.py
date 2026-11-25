import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random


class DQNAgent:
    def __init__(self, config, device: str = 'cpu'):
        if config['args']["dontlearn"]:
            self.epsilon = 0.0
        else:
            self.epsilon = config['epsilon']

    def select_action(self, board, training: bool = True):
        if training:
            epsilon = 0.0
        else:
            epsilon = self.epsilon
