# (generated with --quick)

import hsuanwu.xploit.agent.networks.distributed_actor_critic
import hsuanwu.xploit.agent.networks.off_policy_deterministic_actor
import hsuanwu.xploit.agent.networks.off_policy_double_critic
import hsuanwu.xploit.agent.networks.off_policy_stochastic_actor
import hsuanwu.xploit.agent.networks.on_policy_decoupled_actor_critic
import hsuanwu.xploit.agent.networks.on_policy_shared_actor_critic
import hsuanwu.xploit.agent.networks.utils
from typing import Callable, Type

DistributedActorCritic: Type[hsuanwu.xploit.agent.networks.distributed_actor_critic.DistributedActorCritic]
ExportModel: Type[hsuanwu.xploit.agent.networks.utils.ExportModel]
OffPolicyDeterministicActor: Type[hsuanwu.xploit.agent.networks.off_policy_deterministic_actor.OffPolicyDeterministicActor]
OffPolicyDoubleCritic: Type[hsuanwu.xploit.agent.networks.off_policy_double_critic.OffPolicyDoubleCritic]
OffPolicyStochasticActor: Type[hsuanwu.xploit.agent.networks.off_policy_stochastic_actor.OffPolicyStochasticActor]
OnPolicyDecoupledActorCritic: Type[hsuanwu.xploit.agent.networks.on_policy_decoupled_actor_critic.OnPolicyDecoupledActorCritic]
OnPolicySharedActorCritic: Type[hsuanwu.xploit.agent.networks.on_policy_shared_actor_critic.OnPolicySharedActorCritic]

def get_network_init(method: str = ...) -> Callable: ...
