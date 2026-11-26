import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Optional, Tuple


class DQN(nn.Module):

    def __init__(self, config: Dict):
        self.input_size = config['input_size']  # 16 características
        self.hidden_sizes = config['hidden_sizes']  # [42, 24]
        self.output_size = config['output_size']  # 3 acciones
        self.activation = config.get('activation', 'relu')
        self.weight_init = config.get('weight_init', 'xavier_uniform')

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if not isinstance(x, torch.Tensor):
            x = torch.FloatTensor(x)

            if x.dim() == 1:
                x = x.unsqueeze(0)

        return x
