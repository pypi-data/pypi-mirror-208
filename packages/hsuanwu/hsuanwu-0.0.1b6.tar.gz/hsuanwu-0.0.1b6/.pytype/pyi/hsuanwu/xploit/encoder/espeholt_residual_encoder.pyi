# (generated with --quick)

import gymnasium as gym
import hsuanwu.xploit.encoder.base
import torch as th
from torch import nn
from torch.nn import functional as F
from typing import Any, List, Tuple, Type

BaseEncoder: Type[hsuanwu.xploit.encoder.base.BaseEncoder]
DictConfig: Any

class Conv2d_tf(Any):
    __doc__: str
    padding: Any
    def __init__(self, *args, **kwargs) -> None: ...
    def _compute_padding(self, input, dim) -> Tuple[int, Any]: ...
    def forward(self, input) -> Any: ...

class EspeholtResidualEncoder(hsuanwu.xploit.encoder.base.BaseEncoder):
    __doc__: str
    trunk: Any
    def __init__(self, observation_space, feature_dim: int = ..., net_arch: List[int] = ...) -> None: ...
    def forward(self, obs) -> Any: ...

class ResidualBlock(Any):
    __doc__: str
    conv1: Conv2d_tf
    conv2: Conv2d_tf
    relu: Any
    stride: Any
    def __init__(self, n_channels, stride = ...) -> None: ...
    def forward(self, x) -> Any: ...

class ResidualLayer(Any):
    __doc__: str
    main: Any
    def __init__(self, in_channels, out_channels, stride = ...) -> None: ...
    def forward(self, x) -> Any: ...
