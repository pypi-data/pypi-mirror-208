# (generated with --quick)

import collections
import gymnasium as gym
import hsuanwu.common.engine.base_policy_trainer
import hsuanwu.common.logger
import hydra
import numpy as np
import omegaconf
import os
import pathlib
import threading
import time
import torch as th
import traceback
from torch import multiprocessing as mp
from torch import nn
from typing import Any, Dict, Type

BasePolicyTrainer: Type[hsuanwu.common.engine.base_policy_trainer.BasePolicyTrainer]
Logger: Type[hsuanwu.common.logger.Logger]
Path: Type[pathlib.Path]
deque: Type[collections.deque]

class DistributedTrainer(hsuanwu.common.engine.base_policy_trainer.BasePolicyTrainer):
    __doc__: str
    _agent: Any
    _shared_storages: Any
    _train_env: Any
    def __init__(self, cfgs, train_env, test_env = ...) -> None: ...
    @staticmethod
    def act(cfgs, logger: hsuanwu.common.logger.Logger, gym_env, actor_idx: int, actor_model, free_queue, full_queue, storages: Dict[str, list], init_actor_state_storages: list) -> None: ...
    def save(self) -> None: ...
    def test(self) -> Dict[str, float]: ...
    def train(self) -> None: ...

class Environment:
    __doc__: str
    action_dim: Any
    action_type: str
    env: Any
    episode_return: Any
    episode_step: Any
    def __init__(self, env) -> None: ...
    def _format_obs(self, obs: np.ndarray) -> Any: ...
    def close(self) -> None: ...
    def reset(self, seed) -> Dict[str, Any]: ...
    def step(self, action) -> Dict[str, Any]: ...
