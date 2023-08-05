# (generated with --quick)

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

class ICM(hsuanwu.xplore.reward.base.BaseIntrinsicRewardModule):
    __doc__: str
    batch_size: int
    encoder: Any
    encoder_opt: Any
    fm: Any
    fm_opt: Any
    im: Any
    im_loss: Any
    im_opt: Any
    def __init__(self, observation_space, action_space, device: str = ..., beta: float = ..., kappa: float = ..., latent_dim: int = ..., lr: float = ..., batch_size: int = ...) -> None: ...
    def compute_irs(self, samples: dict, step: int = ...) -> Any: ...
    def update(self, samples: dict) -> None: ...

class InverseDynamicsModel(Any):
    __doc__: str
    trunk: Any
    def __init__(self, latent_dim, action_dim) -> None: ...
    def forward(self, obs, next_obs) -> Any: ...
