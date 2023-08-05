# (generated with --quick)

import gymnasium as gym
import hsuanwu.xploit.storage.base
import threading
import torch as th
from typing import Any, Dict, Generator, Tuple, Type

BaseStorage: Type[hsuanwu.xploit.storage.base.BaseStorage]
DictConfig: Any

class DistributedStorage(hsuanwu.xploit.storage.base.BaseStorage):
    __doc__: str
    _batch_size: int
    _num_steps: int
    _num_storages: int
    storages: Dict[str, list]
    def __init__(self, observation_space, action_space, device: str = ..., num_steps: int = ..., num_storages: int = ..., batch_size: int = ...) -> None: ...
    def add(self, *args) -> None: ...
    @staticmethod
    def sample(device, batch_size: int, free_queue, full_queue, storages: list, init_actor_state_storages: list, lock = ...) -> Tuple[dict, Generator[Any, Any, None]]: ...
    def update(self, *args) -> None: ...
