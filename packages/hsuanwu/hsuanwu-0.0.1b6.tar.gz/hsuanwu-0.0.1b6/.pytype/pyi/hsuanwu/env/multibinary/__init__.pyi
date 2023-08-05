# (generated with --quick)

import gymnasium as gym
import hsuanwu.env.utils
import numpy as np
from typing import Any, Dict, Optional, SupportsFloat, Tuple, Type

AsyncVectorEnv: Any
RecordEpisodeStatistics: Any
SyncVectorEnv: Any
TorchVecEnvWrapper: Type[hsuanwu.env.utils.TorchVecEnvWrapper]

class PixelEnv(Any):
    action_space: Any
    observation_space: Any
    def __init__(self) -> None: ...
    def reset(self, seed: Optional[int] = ..., options = ...) -> Tuple[Any, Dict[str, Any]]: ...
    def step(self, action) -> Tuple[Any, SupportsFloat, bool, bool, Dict[str, Any]]: ...

class StateEnv(Any):
    action_space: Any
    observation_space: Any
    def __init__(self) -> None: ...
    def reset(self, seed: Optional[int] = ..., options = ...) -> Tuple[Any, Dict[str, Any]]: ...
    def step(self, action) -> Tuple[Any, SupportsFloat, bool, bool, Dict[str, Any]]: ...

def make_multibinary_env(env_id: str = ..., num_envs: int = ..., device: str = ..., seed: int = ..., distributed: bool = ...) -> Any: ...
