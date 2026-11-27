import torch
import torch.nn as nn
from typing import Dict


class DQN(nn.Module):

    def __init__(self, config: Dict):
        super(DQN, self).__init__()
        self.input_size = config['input_size']
        self.hidden_sizes = config['hidden_sizes']
        self.output_size = config['output_size']
        self.activation = config.get('activation', 'relu')
        self.weight_init = config.get('weight_init', 'xavier_uniform')

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if not isinstance(x, torch.Tensor):
            x = torch.FloatTensor(x)

            if x.dim() == 1:
                x = x.unsqueeze(0)

        return x
