from typing import List

import torch
from torch import nn

from encoder.transformer_encoder import TransformerEncoder
from decoder.transformer_decoder import TransformerDecoder
from pos_encoder.positional_encoder import PositionalEncoder


class Transformer(nn.Module):
    def __init__(
        self,
        n_layers: int,
        enter_shape: List[int],
        n_blocks: int,
        d_model: int,
        sent_len: int,
        inner_dim: int = 2048,
        dropout: float = 0.1
    ) -> None:
        super().__init__()
        self.n_blocks = n_blocks
        self.n_layers = n_layers
        self.enter_shape = enter_shape
        self.d_model = d_model
        self.sent_len = sent_len
        self.inner_dim = inner_dim

        self.pos_encoder = PositionalEncoder(self.d_model, self.sent_len, dropout)
        self.dropout = nn.Dropout(dropout)
        self.encoders = nn.ModuleList(
            [
                TransformerEncoder(
                    self.n_blocks,
                    self.d_model,
                    self.sent_len,
                    self.enter_shape,
                    self.inner_dim,
                )
                for _ in range(n_layers)
            ]
        )
        self.decoders = nn.ModuleList(
            [
                TransformerDecoder(
                    self.n_blocks,
                    self.d_model,
                    self.sent_len,
                    self.enter_shape,
                    self.inner_dim,
                )
                for _ in range(n_layers)
            ]
        )

        self.linear = nn.Linear(self.d_model, 1)
        self.softmax = nn.Softmax(dim=-1)

    def forward(self, x: List[int] | torch.Tensor) -> torch.Tensor:
        if isinstance(x, list):
            x = torch.unsqueeze(self.pos_encoder(x), 0)
        x = self.dropout(x)

        for i in range(self.n_layers):
            encoder_output, attention = self.encoders[i](x)

        for i in range(self.n_layers):
            x = self.decoders[i](encoder_output, x)

        x = self.linear(x)
        x = self.softmax(x).reshape(x.shape[0], self.sent_len)

        return x
