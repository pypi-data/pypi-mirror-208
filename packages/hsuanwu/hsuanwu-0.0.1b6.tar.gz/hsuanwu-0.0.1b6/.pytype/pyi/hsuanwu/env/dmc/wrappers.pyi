# (generated with --quick)

import glob
import numpy as np
import os
from dm_control import suite
from dm_env import specs
from gymnasium import core
from gymnasium import spaces
from hsuanwu.env.dmc import natural_imgsource
from typing import Annotated, Any, Dict, Tuple, Union

class DMCWrapper(Any):
    _bg_source: Union[natural_imgsource.NoiseSource, natural_imgsource.RandomColorSource, natural_imgsource.RandomImageSource, natural_imgsource.RandomVideoSource]
    _camera_id: Any
    _env: Any
    _frame_skip: Any
    _from_pixels: Any
    _height: Any
    _img_source: Any
    _internal_state_space: Any
    _norm_action_space: Any
    _observation_space: Any
    _true_action_space: Any
    _width: Any
    action_space: Annotated[Any, 'property']
    internal_state_space: Annotated[Any, 'property']
    observation_space: Annotated[Any, 'property']
    def __getattr__(self, name) -> Any: ...
    def __init__(self, domain_name, task_name, resource_files, img_source, total_frames, task_kwargs = ..., visualize_reward = ..., from_pixels = ..., height = ..., width = ..., camera_id = ..., frame_skip = ..., environment_kwargs = ...) -> None: ...
    def _convert_action(self, action) -> Any: ...
    def _get_obs(self, time_step) -> Any: ...
    def render(self, mode = ..., height = ..., width = ..., camera_id = ...) -> Any: ...
    def reset(self, **kwargs) -> Tuple[np.ndarray, dict]: ...
    def seed(self, seed) -> None: ...
    def step(self, action) -> Tuple[Any, Any, bool, bool, Dict[str, Any]]: ...

def _flatten_obs(obs) -> Any: ...
def _spec_to_box(spec) -> Any: ...
