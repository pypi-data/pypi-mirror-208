# (generated with --quick)

import gymnasium as gym
import hsuanwu.env.utils
from typing import Any, Optional, Type

FrameStack: Type[hsuanwu.env.utils.FrameStack]
RecordEpisodeStatistics: Any
SyncVectorEnv: Any
TorchVecEnvWrapper: Type[hsuanwu.env.utils.TorchVecEnvWrapper]
register: Any
registry: Any

def make_dmc_env(env_id: str = ..., num_envs: int = ..., device: str = ..., resource_files: Optional[list] = ..., img_source: Optional[str] = ..., total_frames: Optional[int] = ..., seed: int = ..., visualize_reward: bool = ..., from_pixels: bool = ..., height: int = ..., width: int = ..., camera_id: int = ..., frame_stack: int = ..., frame_skip: int = ..., episode_length: int = ..., environment_kwargs: Optional[dict] = ...) -> Any: ...
