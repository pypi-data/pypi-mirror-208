# (generated with --quick)

import abc
import gymnasium as gym
import hsuanwu.common.logger
import hsuanwu.common.timer
import numpy as np
import omegaconf
import os
import pathlib
import pynvml
import random
import torch as th
from typing import Annotated, Any, Callable, Dict, Optional, Type, TypeVar, Union

ABC: Type[abc.ABC]
ALL_DEFAULT_CFGS: Dict[str, Any]
Logger: Type[hsuanwu.common.logger.Logger]
OmegaConf: Any
Path: Type[pathlib.Path]
Timer: Type[hsuanwu.common.timer.Timer]
_MANDATORY_CFGS: Dict[str, Optional[Union[int, str, Dict[str, None]]]]

_FuncT = TypeVar('_FuncT', bound=Callable)

class BasePolicyTrainer(abc.ABC):
    __doc__: str
    _action_range: Any
    _cfgs: Any
    _device: Any
    _global_episode: int
    _global_step: int
    _logger: hsuanwu.common.logger.Logger
    _num_test_episodes: Any
    _num_train_steps: Any
    _seed: Any
    _test_env: Any
    _test_every_episodes: Any
    _test_every_steps: Any
    _timer: hsuanwu.common.timer.Timer
    _train_env: Any
    _work_dir: pathlib.Path
    global_episode: Annotated[int, 'property']
    global_step: Annotated[int, 'property']
    def __init__(self, cfgs, train_env, test_env = ...) -> None: ...
    def _check_cfgs(self, cfgs) -> None: ...
    def _process_cfgs(self, cfgs) -> Any: ...
    def _set_class_path(self, cfgs) -> Any: ...
    @abstractmethod
    def save(self) -> None: ...
    @abstractmethod
    def test(self) -> Optional[Dict[str, float]]: ...
    @abstractmethod
    def train(self) -> Optional[Dict[str, float]]: ...

def abstractmethod(funcobj: _FuncT) -> _FuncT: ...
