# (generated with --quick)

import gymnasium as gym
import hsuanwu.xploit.storage.base
import torch as th
from typing import Any, Type

BaseStorage: Type[hsuanwu.xploit.storage.base.BaseStorage]
BatchSampler: Any
DictConfig: Any
SubsetRandomSampler: Any

class VanillaRolloutStorage(hsuanwu.xploit.storage.base.BaseStorage):
    __doc__: str
    _batch_size: int
    _discount: float
    _gae_lambda: float
    _global_step: int
    _num_envs: int
    _num_steps: int
    actions: Any
    advantages: Any
    log_probs: Any
    obs: Any
    returns: Any
    rewards: Any
    terminateds: Any
    truncateds: Any
    values: Any
    def __init__(self, observation_space, action_space, device: str = ..., num_steps: int = ..., num_envs: int = ..., batch_size: int = ..., discount: float = ..., gae_lambda: float = ...) -> None: ...
    def add(self, obs, actions, rewards, terminateds, truncateds, next_obs, log_probs, values) -> None: ...
    def compute_returns_and_advantages(self, last_values) -> None: ...
    def sample(self) -> generator: ...
    def update(self) -> None: ...
