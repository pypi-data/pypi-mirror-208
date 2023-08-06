# (generated with --quick)

import abc
import gymnasium as gym
import torch as th
from typing import Any, Callable, Type, TypeVar

ABC: Type[abc.ABC]
DictConfig: Any

_FuncT = TypeVar('_FuncT', bound=Callable)

class BaseIntrinsicRewardModule(abc.ABC):
    __doc__: str
    _action_dim: Any
    _action_shape: Any
    _action_type: Any
    _beta: float
    _device: Any
    _kappa: float
    _obs_shape: Any
    def __init__(self, observation_space, action_space, device: str = ..., beta: float = ..., kappa: float = ...) -> None: ...
    @abstractmethod
    def compute_irs(self, samples: dict, step: int = ...) -> Any: ...
    @abstractmethod
    def update(self, samples: dict) -> None: ...

def abstractmethod(funcobj: _FuncT) -> _FuncT: ...
