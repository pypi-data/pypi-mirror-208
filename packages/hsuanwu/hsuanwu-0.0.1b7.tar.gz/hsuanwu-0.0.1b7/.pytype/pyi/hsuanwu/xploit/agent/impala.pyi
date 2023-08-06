# (generated with --quick)

import gymnasium as gym
import hsuanwu.xploit.agent.base
import hsuanwu.xploit.agent.networks.distributed_actor_critic
import os
import pathlib
import threading
import torch as th
from torch import nn
from torch.nn import functional as F
from typing import Any, Callable, Dict, Optional, Tuple, Type, TypeVar

BaseAgent: Type[hsuanwu.xploit.agent.base.BaseAgent]
DictConfig: Any
DistributedActorCritic: Type[hsuanwu.xploit.agent.networks.distributed_actor_critic.DistributedActorCritic]
Path: Type[pathlib.Path]

_T = TypeVar('_T')

class IMPALA(hsuanwu.xploit.agent.base.BaseAgent):
    __doc__: str
    actor: hsuanwu.xploit.agent.networks.distributed_actor_critic.DistributedActorCritic
    baseline_coef: float
    discount: float
    dist: Any
    ent_coef: float
    learner: hsuanwu.xploit.agent.networks.distributed_actor_critic.DistributedActorCritic
    lr_scheduler: Any
    max_grad_norm: float
    network_init_method: str
    opt: Any
    training: bool
    def __init__(self, observation_space, action_space, device: str, feature_dim: int, lr: float = ..., eps: float = ..., use_lstm: bool = ..., ent_coef: float = ..., baseline_coef: float = ..., max_grad_norm: float = ..., discount: float = ..., network_init_method: str = ...) -> None: ...
    def act(self, *kwargs) -> None: ...
    def integrate(self, **kwargs) -> None: ...
    def load(self, path: str) -> None: ...
    def save(self, path: pathlib.Path) -> None: ...
    def train(self, training: bool = ...) -> None: ...
    def update(self, actor_model, learner_model, batch: dict, init_actor_states: tuple, optimizer, lr_scheduler, lock = ...) -> Dict[str, tuple]: ...

class VTraceLoss:
    clip_pg_rho_threshold: Any
    clip_rho_threshold: Any
    dist: None
    def __call__(self, batch) -> Tuple[Any, Any, Any]: ...
    def __init__(self, clip_rho_threshold = ..., clip_pg_rho_threshold = ...) -> None: ...
    def compute_ISW(self, target_dist, behavior_dist, action) -> Any: ...

def deepcopy(x: _T, memo: Optional[Dict[int, Any]] = ..., _nil = ...) -> _T: ...
def get_network_init(method: str = ...) -> Callable: ...
