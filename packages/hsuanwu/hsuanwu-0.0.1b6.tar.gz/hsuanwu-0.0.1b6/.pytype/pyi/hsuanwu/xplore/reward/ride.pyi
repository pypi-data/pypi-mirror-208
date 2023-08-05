# (generated with --quick)

import collections
import gymnasium as gym
import hsuanwu.xplore.reward.base
import numpy as np
import torch as th
from torch import nn
from torch.nn import functional as F
from typing import Any, Type

BaseIntrinsicRewardModule: Type[hsuanwu.xplore.reward.base.BaseIntrinsicRewardModule]
DataLoader: Any
DictConfig: Any
TensorDataset: Any
deque: Type[collections.deque]

class Encoder(Any):
    __doc__: str
    linear: Any
    trunk: Any
    def __init__(self, obs_shape: tuple, action_dim: int, latent_dim: int) -> None: ...
    def forward(self, obs) -> Any: ...

class ForwardDynamicsModel(Any):
    __doc__: str
    trunk: Any
    def __init__(self, latent_dim, action_dim) -> None: ...
    def forward(self, obs, pred_actions) -> Any: ...

class InverseDynamicsModel(Any):
    __doc__: str
    trunk: Any
    def __init__(self, latent_dim, action_dim) -> None: ...
    def forward(self, obs, next_obs) -> Any: ...

class RIDE(hsuanwu.xplore.reward.base.BaseIntrinsicRewardModule):
    __doc__: str
    batch_size: int
    c: float
    encoder: Any
    encoder_opt: Any
    episodic_memory: collections.deque
    fm: Any
    fm_opt: Any
    im: Any
    im_loss: Any
    im_opt: Any
    k: int
    kernel_cluster_distance: float
    kernel_epsilon: float
    sm: float
    def __init__(self, observation_space, action_space, device: str = ..., beta: float = ..., kappa: float = ..., latent_dim: int = ..., lr: float = ..., batch_size: int = ..., capacity: int = ..., k: int = ..., kernel_cluster_distance: float = ..., kernel_epsilon: float = ..., c: float = ..., sm: float = ...) -> None: ...
    def compute_irs(self, samples: dict, step: int = ...) -> Any: ...
    def pseudo_counts(self, e) -> Any: ...
    def update(self, samples: dict) -> None: ...
