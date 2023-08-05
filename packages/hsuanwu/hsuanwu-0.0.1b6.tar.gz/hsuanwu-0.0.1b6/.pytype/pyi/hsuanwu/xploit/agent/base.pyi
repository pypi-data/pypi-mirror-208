# (generated with --quick)

import abc
import gymnasium as gym
import pathlib
import torch as th
from typing import Any, Callable, Dict, Type, TypeVar

ABC: Type[abc.ABC]
DictConfig: Any
Path: Type[pathlib.Path]

_FuncT = TypeVar('_FuncT', bound=Callable)

class BaseAgent(abc.ABC):
    __doc__: str
    action_dim: Any
    action_range: Any
    action_shape: Any
    action_type: Any
    aug: None
    device: Any
    dist: None
    encoder: None
    eps: float
    feature_dim: int
    irs: None
    lr: float
    obs_shape: Any
    training: bool
    def __init__(self, observation_space, action_space, device: str, feature_dim: int, lr: float, eps: float) -> None: ...
    @abstractmethod
    def act(self, obs, training: bool = ..., step: int = ...) -> Any: ...
    @abstractmethod
    def integrate(self, **kwargs) -> None: ...
    @abstractmethod
    def load(self, path: str) -> None: ...
    @abstractmethod
    def save(self, path: pathlib.Path) -> None: ...
    @abstractmethod
    def train(self, training: bool = ...) -> None: ...
    @abstractmethod
    def update(self, **kwargs) -> Dict[str, float]: ...

def abstractmethod(funcobj: _FuncT) -> _FuncT: ...
