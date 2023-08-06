# (generated with --quick)

import collections
import gymnasium as gym
import numpy as np
import torch as th
from typing import Any, Callable, List, Optional, Tuple, Type, Union

AsyncVectorEnv: Any
OmegaConf: Any
RecordEpisodeStatistics: Any
SyncVectorEnv: Any
VectorEnv: Any
deque: Type[collections.deque]

class FrameStack(Any):
    __doc__: str
    _frames: collections.deque
    _k: int
    observation_space: Any
    def __init__(self, env, k: int) -> None: ...
    def _get_obs(self) -> np.ndarray: ...
    def reset(self, **kwargs) -> Tuple[Any, dict]: ...
    def step(self, action: Tuple[float]) -> Tuple[Any, float, bool, bool, dict]: ...

class HsuanwuEnvWrapper(Any):
    __doc__: str
    def __init__(self, env_fn: Callable, num_envs: int = ..., device: str = ..., parallel: bool = ...) -> None: ...

class TorchVecEnvWrapper(Any):
    __doc__: str
    action_space: Any
    device: Any
    num_envs: Any
    observation_space: Any
    def __init__(self, env, device: str) -> None: ...
    def reset(self, seed: Optional[Union[int, List[int]]] = ..., options: Optional[dict] = ...) -> Tuple[Any, dict]: ...
    def step(self, actions) -> Tuple[Any, Any, Any, bool, dict]: ...
