# (generated with --quick)

import gymnasium as gym
import hsuanwu.xploit.encoder.base
import torch as th
from torch import nn
from typing import Any, Type

BaseEncoder: Type[hsuanwu.xploit.encoder.base.BaseEncoder]
DictConfig: Any

class MnihCnnEncoder(hsuanwu.xploit.encoder.base.BaseEncoder):
    __doc__: str
    trunk: Any
    def __init__(self, observation_space, feature_dim: int = ...) -> None: ...
    def forward(self, obs) -> Any: ...
