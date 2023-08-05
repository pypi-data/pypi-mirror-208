# (generated with --quick)

import gymnasium as gym
import hsuanwu.xploit.agent.base
import hsuanwu.xploit.agent.networks.off_policy_double_critic
import hsuanwu.xploit.agent.networks.off_policy_stochastic_actor
import hsuanwu.xploit.agent.networks.utils
import numpy as np
import os
import pathlib
import torch as th
from hsuanwu.xploit.agent import utils
from torch.nn import functional as F
from typing import Annotated, Any, Callable, Dict, Tuple, Type

BaseAgent: Type[hsuanwu.xploit.agent.base.BaseAgent]
DictConfig: Any
ExportModel: Type[hsuanwu.xploit.agent.networks.utils.ExportModel]
OffPolicyDoubleCritic: Type[hsuanwu.xploit.agent.networks.off_policy_double_critic.OffPolicyDoubleCritic]
OffPolicyStochasticActor: Type[hsuanwu.xploit.agent.networks.off_policy_stochastic_actor.OffPolicyStochasticActor]
Path: Type[pathlib.Path]

class SAC(hsuanwu.xploit.agent.base.BaseAgent):
    __doc__: str
    actor: Any
    actor_opt: Any
    alpha: Annotated[Any, 'property']
    aug: Any
    betas: Tuple[float, ...]
    critic: Any
    critic_opt: Any
    critic_target: Any
    critic_target_tau: float
    discount: float
    dist: Any
    encoder: Any
    encoder_opt: Any
    fixed_temperature: bool
    irs: Any
    log_alpha: Any
    log_alpha_opt: Any
    network_init_method: str
    target_entropy: Any
    training: bool
    update_every_steps: int
    def __init__(self, observation_space, action_space, device: str, feature_dim: int, lr: float = ..., eps: float = ..., hidden_dim: int = ..., critic_target_tau: float = ..., update_every_steps: int = ..., log_std_range: Tuple[float, ...] = ..., betas: Tuple[float, ...] = ..., temperature: float = ..., fixed_temperature: bool = ..., discount: float = ..., network_init_method: str = ...) -> None: ...
    def act(self, obs, training: bool = ..., step: int = ...) -> Tuple[Any]: ...
    def integrate(self, **kwargs) -> None: ...
    def load(self, path: str) -> None: ...
    def save(self, path: pathlib.Path) -> None: ...
    def train(self, training: bool = ...) -> None: ...
    def update(self, replay_storage, step: int = ...) -> Dict[str, float]: ...
    def update_actor_and_alpha(self, obs, weights, step: int) -> Dict[str, float]: ...
    def update_critic(self, obs, action, reward, terminated, next_obs, weights, aug_obs, aug_next_obs, step: int) -> Dict[str, float]: ...

def get_network_init(method: str = ...) -> Callable: ...
