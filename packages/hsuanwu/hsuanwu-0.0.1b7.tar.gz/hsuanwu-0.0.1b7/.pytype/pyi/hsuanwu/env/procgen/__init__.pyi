# (generated with --quick)

import gymnasium as gym
import hsuanwu.env.utils
import numpy as np
from typing import Any, Tuple, Type

Box: Any
NormalizeReward: Any
ProcgenEnv: Any
RecordEpisodeStatistics: Any
TorchVecEnvWrapper: Type[hsuanwu.env.utils.TorchVecEnvWrapper]
TransformObservation: Any
TransformReward: Any

class AdapterEnv(Any):
    __doc__: str
    is_vector_env: bool
    num_envs: int
    single_action_space: Any
    single_observation_space: Any
    def __init__(self, env, num_envs: int) -> None: ...
    def reset(self, **kwargs) -> Tuple[np.ndarray, dict]: ...
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, dict]: ...

def make_procgen_env(env_id: str = ..., num_envs: int = ..., device: str = ..., seed: int = ..., gamma: float = ..., num_levels: int = ..., start_level: int = ..., distribution_mode: str = ...) -> Any: ...
