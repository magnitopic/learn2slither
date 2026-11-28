import torch
import torch.nn as nn
from typing import Dict

ACTIVATIONS = {
    'relu': nn.ReLU,
    'tanh': nn.Tanh,
    'leaky_relu': nn.LeakyReLU,
}


class DQN(nn.Module):

    def __init__(self, config: Dict):
        super(DQN, self).__init__()
        self.input_size = config['input_size']
        self.hidden_sizes = config['hidden_sizes']
        self.output_size = config['output_size']
        self.activation = config.get('activation', 'relu')
        self.weight_init = config.get('weight_init', 'xavier_uniform')

        if self.activation not in ACTIVATIONS:
            raise ValueError(f"Unknown activation: {self.activation}")

        # input -> hidden layers -> one Q-value per action
        sizes = [self.input_size, *self.hidden_sizes]
        layers = []
        for in_size, out_size in zip(sizes[:-1], sizes[1:]):
            layers.append(nn.Linear(in_size, out_size))
            layers.append(ACTIVATIONS[self.activation]())
        layers.append(nn.Linear(sizes[-1], self.output_size))

        self.network = nn.Sequential(*layers)
        self.init_weights()

    def init_weights(self):
        for module in self.network:
            if not isinstance(module, nn.Linear):
                continue
            if self.weight_init == 'xavier_uniform':
                nn.init.xavier_uniform_(module.weight)
            elif self.weight_init == 'kaiming_uniform':
                nn.init.kaiming_uniform_(module.weight, nonlinearity='relu')
            nn.init.zeros_(module.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if not isinstance(x, torch.Tensor):
            x = torch.FloatTensor(x)

        # A single state becomes a batch of one
        if x.dim() == 1:
            x = x.unsqueeze(0)

        return self.network(x)
