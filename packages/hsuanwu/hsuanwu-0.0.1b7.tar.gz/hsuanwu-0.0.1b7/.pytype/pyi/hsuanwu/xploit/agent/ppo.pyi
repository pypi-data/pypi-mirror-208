# (generated with --quick)

import gymnasium as gym
import hsuanwu.xploit.agent.base
import hsuanwu.xploit.agent.networks.on_policy_shared_actor_critic
import hsuanwu.xploit.storage.vanilla_rollout_storage
import numpy as np
import os
import pathlib
import torch as th
from torch import nn
from typing import Any, Callable, Dict, Type, Union

BaseAgent: Type[hsuanwu.xploit.agent.base.BaseAgent]
DictConfig: Any
OnPolicySharedActorCritic: Type[hsuanwu.xploit.agent.networks.on_policy_shared_actor_critic.OnPolicySharedActorCritic]
Path: Type[pathlib.Path]
Storage: Type[hsuanwu.xploit.storage.vanilla_rollout_storage.VanillaRolloutStorage]

class PPO(hsuanwu.xploit.agent.base.BaseAgent):
    __doc__: str
    ac: hsuanwu.xploit.agent.networks.on_policy_shared_actor_critic.OnPolicySharedActorCritic
    ac_opt: Any
    aug: Any
    aug_coef: float
    clip_range: float
    clip_range_vf: float
    dist: Any
    ent_coef: float
    irs: Any
    max_grad_norm: float
    n_epochs: int
    network_init_method: str
    training: bool
    vf_coef: float
    def __init__(self, observation_space, action_space, device: str, feature_dim: int, lr: float = ..., eps: float = ..., hidden_dim: int = ..., clip_range: float = ..., clip_range_vf: float = ..., n_epochs: int = ..., vf_coef: float = ..., ent_coef: float = ..., aug_coef: float = ..., max_grad_norm: float = ..., network_init_method: str = ...) -> None: ...
    def act(self, obs, training: bool = ..., step: int = ...) -> Union[tuple, Dict[str, Any]]: ...
    def get_value(self, obs) -> Any: ...
    def integrate(self, **kwargs) -> None: ...
    def load(self, path: str) -> None: ...
    def save(self, path: pathlib.Path) -> None: ...
    def train(self, training: bool = ...) -> None: ...
    def update(self, rollout_storage: hsuanwu.xploit.storage.vanilla_rollout_storage.VanillaRolloutStorage, episode: int = ...) -> Dict[str, float]: ...

def get_network_init(method: str = ...) -> Callable: ...
