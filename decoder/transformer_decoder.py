from typing import List

import torch
from torch import nn

from attention import *
from normalization import *
from feed_forward import *


class TransformerDecoder(nn.Module):
    def __init__(
        self,
        n_blocks: int,
        d_model: int,
        sen_len: int,
        enter_shape: List[int],
        inner_dim: int = 2048,
    ) -> None:
        super().__init__()
        self.multi_head = MultiHeadAttention(d_model, sen_len, n_blocks)
        self.add_norm_1 = AddNorm(enter_shape)
        self.feed_forward = PositionWiseFFN(d_model, inner_dim)
        self.add_norm_2 = AddNorm(enter_shape)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        ...
