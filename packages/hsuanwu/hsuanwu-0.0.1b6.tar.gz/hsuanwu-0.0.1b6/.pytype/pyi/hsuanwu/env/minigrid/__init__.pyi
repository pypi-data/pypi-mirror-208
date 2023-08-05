# (generated with --quick)

import gymnasium as gym
import hsuanwu.env.utils
import numpy as np
from typing import Any, Type

AsyncVectorEnv: Any
FlatObsWrapper: Any
FrameStack: Type[hsuanwu.env.utils.FrameStack]
FullyObsWrapper: Any
RecordEpisodeStatistics: Any
SyncVectorEnv: Any
TorchVecEnvWrapper: Type[hsuanwu.env.utils.TorchVecEnvWrapper]

class Minigrid2Image(Any):
    observation_space: Any
    def __init__(self, env) -> None: ...
    def observation(self, observation) -> Any: ...

def make_minigrid_env(env_id: str = ..., num_envs: int = ..., fully_observable: bool = ..., seed: int = ..., frame_stack: int = ..., device: str = ..., distributed: bool = ...) -> Any: ...
