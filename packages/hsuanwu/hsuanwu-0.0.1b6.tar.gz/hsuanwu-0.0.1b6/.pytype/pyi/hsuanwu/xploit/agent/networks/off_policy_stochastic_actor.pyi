# (generated with --quick)

import torch as th
from torch import nn
from typing import Any

Distribution: Any

class OffPolicyStochasticActor(Any):
    __doc__: str
    dist: None
    log_std_max: Any
    log_std_min: Any
    policy: Any
    def __init__(self, action_dim: int, feature_dim: int = ..., hidden_dim: int = ..., log_std_range: tuple = ...) -> None: ...
    def forward(self, obs) -> Any: ...
    def get_dist(self, obs, step: int) -> Any: ...
