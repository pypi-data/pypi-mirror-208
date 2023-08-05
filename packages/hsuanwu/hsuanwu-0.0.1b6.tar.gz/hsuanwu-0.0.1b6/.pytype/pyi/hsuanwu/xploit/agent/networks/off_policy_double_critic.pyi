# (generated with --quick)

import torch as th
from torch import nn
from typing import Any

class OffPolicyDoubleCritic(Any):
    Q1: Any
    Q2: Any
    __doc__: str
    def __init__(self, action_dim: int, feature_dim: int = ..., hidden_dim: int = ...) -> None: ...
    def forward(self, obs, action) -> tuple: ...
