# (generated with --quick)

import collections
import gymnasium as gym
import hsuanwu.xploit.storage.base
import numpy as np
import torch as th
from typing import Any, Type

BaseStorage: Type[hsuanwu.xploit.storage.base.BaseStorage]
DictConfig: Any
deque: Type[collections.deque]

class PrioritizedReplayStorage(hsuanwu.xploit.storage.base.BaseStorage):
    __doc__: str
    _alpha: float
    _batch_size: int
    _beta: float
    _position: int
    _priorities: Any
    _storage: collections.deque
    _storage_size: int
    def __init__(self, observation_space, action_space, device: str = ..., storage_size: int = ..., batch_size: int = ..., alpha: float = ..., beta: float = ...) -> None: ...
    def __len__(self) -> int: ...
    def add(self, obs, action, reward, terminated, info, next_obs) -> None: ...
    def annealing_beta(self, step: int) -> float: ...
    def sample(self, step: int) -> tuple: ...
    def update(self, metrics: dict) -> None: ...
