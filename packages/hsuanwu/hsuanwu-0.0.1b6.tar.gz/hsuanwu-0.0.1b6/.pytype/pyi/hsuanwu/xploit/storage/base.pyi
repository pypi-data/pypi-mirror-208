# (generated with --quick)

import abc
import gymnasium as gym
import torch as th
from typing import Any, Callable, Type, TypeVar

ABC: Type[abc.ABC]
DictConfig: Any

_FuncT = TypeVar('_FuncT', bound=Callable)

class BaseStorage(abc.ABC):
    __doc__: str
    _action_dim: Any
    _action_range: Any
    _action_shape: Any
    _action_type: Any
    _device: Any
    _obs_shape: Any
    def __init__(self, observation_space, action_space, device: str = ...) -> None: ...
    @abstractmethod
    def add(self, *args) -> None: ...
    @abstractmethod
    def sample(self, *args) -> Any: ...
    @abstractmethod
    def update(self, *args) -> None: ...

def abstractmethod(funcobj: _FuncT) -> _FuncT: ...
