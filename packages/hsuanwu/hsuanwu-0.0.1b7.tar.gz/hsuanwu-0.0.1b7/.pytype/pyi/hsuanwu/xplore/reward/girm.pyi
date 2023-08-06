# (generated with --quick)

import gymnasium as gym
import hsuanwu.xplore.reward.base
import numpy as np
import torch as th
from torch import nn
from torch import optim
from torch.nn import functional as F
from typing import Any, Type

BaseIntrinsicRewardModule: Type[hsuanwu.xplore.reward.base.BaseIntrinsicRewardModule]
DataLoader: Any
DictConfig: Any
TensorDataset: Any
Variable: Any

class Decoder(Any):
    __doc__: str
    trunk: Any
    def __init__(self, action_dim: int, latent_dim: int) -> None: ...
    def forward(self, obs, z) -> Any: ...

class Encoder(Any):
    __doc__: str
    head: Any
    linear: Any
    trunk: Any
    def __init__(self, obs_shape: tuple, action_dim: int, latent_dim: int) -> None: ...
    def encode(self, obs) -> Any: ...
    def forward(self, obs, next_obs) -> Any: ...

class GIRM(hsuanwu.xplore.reward.base.BaseIntrinsicRewardModule):
    __doc__: str
    action_loss: Any
    batch_size: int
    kld_loss_beta: float
    lambd: float
    lambd_action: float
    lambd_recon: float
    opt: Any
    vae: VAE
    def __init__(self, observation_space, action_space, device: str = ..., beta: float = ..., kappa: float = ..., latent_dim: int = ..., lr: float = ..., batch_size: int = ..., lambd: float = ..., lambd_recon: float = ..., lambd_action: float = ..., kld_loss_beta: float = ...) -> None: ...
    def compute_irs(self, samples: dict, step: int = ...) -> Any: ...
    def get_vae_loss(self, recon_x, x, mean, logvar) -> Any: ...
    def update(self, samples: dict) -> None: ...

class VAE(Any):
    __doc__: str
    _device: Any
    decoder: Decoder
    encoder: Encoder
    latent_dim: int
    logvar: Any
    mu: Any
    def __init__(self, device, obs_shape: tuple, action_dim: int, latent_dim: int) -> None: ...
    def forward(self, obs, next_obs) -> tuple: ...
    def reparameterize(self, mu, logvar, device, training: bool = ...) -> Any: ...
