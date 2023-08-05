# (generated with --quick)

import collections
import gymnasium as gym
import hsuanwu.common.engine.base_policy_trainer
import hsuanwu.common.engine.utils
import hydra
import numpy as np
import omegaconf
import pathlib
import torch as th
from typing import Any, Dict, Type

BasePolicyTrainer: Type[hsuanwu.common.engine.base_policy_trainer.BasePolicyTrainer]
Path: Type[pathlib.Path]
deque: Type[collections.deque]
eval_mode: Type[hsuanwu.common.engine.utils.eval_mode]

class OnPolicyTrainer(hsuanwu.common.engine.base_policy_trainer.BasePolicyTrainer):
    __doc__: str
    _agent: Any
    _global_episode: int
    _global_step: Any
    _num_envs: Any
    _num_steps: Any
    _rollout_storage: Any
    def __init__(self, cfgs, train_env, test_env = ...) -> None: ...
    def save(self) -> None: ...
    def test(self) -> Dict[str, float]: ...
    def train(self) -> None: ...
