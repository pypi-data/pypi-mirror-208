# (generated with --quick)

import torch as th
from torch import nn
from typing import Any

Distribution: Any

class OffPolicyDeterministicActor(Any):
    __doc__: str
    dist: None
    policy: Any
    def __init__(self, action_dim: int, feature_dim: int = ..., hidden_dim: int = ...) -> None: ...
    def forward(self, obs) -> Any: ...
    def get_dist(self, obs, step: int) -> Any: ...
