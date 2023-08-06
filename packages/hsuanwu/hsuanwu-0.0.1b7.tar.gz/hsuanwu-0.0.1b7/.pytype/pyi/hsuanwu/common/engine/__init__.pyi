# (generated with --quick)

import gymnasium as gym
import hsuanwu.common.engine.base_policy_trainer
import hsuanwu.common.engine.distributed_trainer
import hsuanwu.common.engine.off_policy_trainer
import hsuanwu.common.engine.on_policy_trainer
import omegaconf
from typing import Any, Dict, Type, Union

ALL_DEFAULT_CFGS: Dict[str, Any]
BasePolicyTrainer: Type[hsuanwu.common.engine.base_policy_trainer.BasePolicyTrainer]
DistributedTrainer: Type[hsuanwu.common.engine.distributed_trainer.DistributedTrainer]
OffPolicyTrainer: Type[hsuanwu.common.engine.off_policy_trainer.OffPolicyTrainer]
OnPolicyTrainer: Type[hsuanwu.common.engine.on_policy_trainer.OnPolicyTrainer]

class HsuanwuEngine:
    __doc__: str
    trainer: Union[hsuanwu.common.engine.distributed_trainer.DistributedTrainer, hsuanwu.common.engine.off_policy_trainer.OffPolicyTrainer, hsuanwu.common.engine.on_policy_trainer.OnPolicyTrainer]
    def __init__(self, cfgs, train_env, test_env = ...) -> None: ...
    def invoke(self) -> None: ...
