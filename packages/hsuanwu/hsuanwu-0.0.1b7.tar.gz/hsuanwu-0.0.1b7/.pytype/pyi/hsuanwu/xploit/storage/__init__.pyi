# (generated with --quick)

import hsuanwu.xploit.storage.base
import hsuanwu.xploit.storage.distributed_storage
import hsuanwu.xploit.storage.nstep_replay_storage
import hsuanwu.xploit.storage.prioritized_replay_storage
import hsuanwu.xploit.storage.vanilla_replay_storage
import hsuanwu.xploit.storage.vanilla_rollout_storage
from typing import Type

BaseStorage: Type[hsuanwu.xploit.storage.base.BaseStorage]
DistributedStorage: Type[hsuanwu.xploit.storage.distributed_storage.DistributedStorage]
NStepReplayStorage: Type[hsuanwu.xploit.storage.nstep_replay_storage.NStepReplayStorage]
PrioritizedReplayStorage: Type[hsuanwu.xploit.storage.prioritized_replay_storage.PrioritizedReplayStorage]
VanillaReplayStorage: Type[hsuanwu.xploit.storage.vanilla_replay_storage.VanillaReplayStorage]
VanillaRolloutStorage: Type[hsuanwu.xploit.storage.vanilla_rollout_storage.VanillaRolloutStorage]
