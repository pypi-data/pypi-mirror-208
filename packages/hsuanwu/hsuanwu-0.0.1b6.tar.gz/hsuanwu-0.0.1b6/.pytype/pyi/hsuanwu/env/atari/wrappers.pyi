# (generated with --quick)

import gymnasium as gym
import numpy as np
from typing import Any, Tuple

class EpisodicLifeEnv(Any):
    __doc__: str
    lives: Any
    was_real_done: Any
    def __init__(self, env) -> None: ...
    def reset(self, **kwargs) -> Tuple[np.ndarray, dict]: ...
    def step(self, action: int) -> Tuple[Any, float, bool, bool, dict]: ...

class FireResetEnv(Any):
    __doc__: str
    def __init__(self, env) -> None: ...
    def reset(self, **kwargs) -> Tuple[np.ndarray, dict]: ...

class MaxAndSkipEnv(Any):
    __doc__: str
    _obs_buffer: Any
    _skip: int
    def __init__(self, env, skip: int = ...) -> None: ...
    def step(self, action: int) -> Tuple[Any, float, bool, bool, dict]: ...

class NoopResetEnv(Any):
    __doc__: str
    noop_action: int
    noop_max: int
    override_num_noops: None
    def __init__(self, env, noop_max: int = ...) -> None: ...
    def reset(self, **kwargs) -> Tuple[np.ndarray, dict]: ...
