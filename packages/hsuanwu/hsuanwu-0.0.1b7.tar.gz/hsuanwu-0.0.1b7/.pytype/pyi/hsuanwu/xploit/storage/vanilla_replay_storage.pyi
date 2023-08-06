# (generated with --quick)

import gymnasium as gym
import hsuanwu.xploit.storage.base
import numpy as np
import torch as th
from typing import Any, Type

BaseStorage: Type[hsuanwu.xploit.storage.base.BaseStorage]
DictConfig: Any

class VanillaReplayStorage(hsuanwu.xploit.storage.base.BaseStorage):
    __doc__: str
    _batch_size: int
    _full: bool
    _global_step: int
    _storage_size: int
    actions: Any
    obs: Any
    rewards: Any
    terminateds: Any
    def __init__(self, observation_space, action_space, device: str = ..., storage_size: int = ..., batch_size: int = ...) -> None: ...
    def __len__(self) -> int: ...
    def add(self, obs, action, reward, terminated, info, next_obs) -> None: ...
    def sample(self, step: int) -> tuple: ...
    def update(self, *args) -> None: ...
