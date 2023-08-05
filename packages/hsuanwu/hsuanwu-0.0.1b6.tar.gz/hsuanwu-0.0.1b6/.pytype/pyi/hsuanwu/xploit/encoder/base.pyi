# (generated with --quick)

import gymnasium as gym
from torch import nn
from typing import Annotated, Any

DictConfig: Any

class BaseEncoder(Any):
    __doc__: str
    _feature_dim: int
    _observation_space: Any
    feature_dim: Annotated[int, 'property']
    def __init__(self, observation_space, feature_dim: int = ...) -> None: ...
