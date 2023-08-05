import os
from pathlib import Path
from typing import Any, Dict, Tuple, Union

import gymnasium as gym
import numpy as np
import torch as th
from omegaconf import DictConfig
from torch import nn

from hsuanwu.xploit.agent.base import BaseAgent
from hsuanwu.xploit.agent.networks import OnPolicySharedActorCritic, get_network_init
from hsuanwu.xploit.storage import VanillaRolloutStorage as Storage


class PPG(BaseAgent):
    """Phasic Policy Gradient (PPG) agent.
        Based on: https://github.com/vwxyzjn/cleanrl/blob/master/cleanrl/ppg_procgen.py

    Args:
        observation_space (Space or DictConfig): The observation space of environment. When invoked by Hydra,
            'observation_space' is a 'DictConfig' like {"shape": observation_space.shape, }.
        action_space (Space or DictConfig): The action space of environment. When invoked by Hydra,
            'action_space' is a 'DictConfig' like
            {"shape": action_space.shape, "n": action_space.n, "type": "Discrete", "range": [0, n - 1]} or
            {"shape": action_space.shape, "type": "Box", "range": [action_space.low[0], action_space.high[0]]}.
        device (str): Device (cpu, cuda, ...) on which the code should be run.
        feature_dim (int): Number of features extracted by the encoder.
        lr (float): The learning rate.
        eps (float): Term added to the denominator to improve numerical stability.

        hidden_dim (int): The size of the hidden layers.
        clip_range (float): Clipping parameter.
        clip_range_vf (float): Clipping parameter for the value function.
        vf_coef (float): Weighting coefficient of value loss.
        ent_coef (float): Weighting coefficient of entropy bonus.
        aug_coef (float): Weighting coefficient of augmentation loss.
        max_grad_norm (float): Maximum norm of gradients.
        policy_epochs (int): Number of iterations in the policy phase.
        aux_epochs (int): Number of iterations in the auxiliary phase.
        kl_coef (float): Weighting coefficient of divergence loss.
        num_aux_mini_batch (int) Number of mini-batches in auxiliary phase.
        num_aux_grad_accum (int): Number of gradient accumulation for auxiliary phase update.
        network_init_method (str): Network initialization method name.

    Returns:
        PPG agent instance.
    """

    def __init__(
        self,
        observation_space: Union[gym.Space, DictConfig],
        action_space: Union[gym.Space, DictConfig],
        device: str,
        feature_dim: int,
        lr: float = 5e-4,
        eps: float = 1e-5,
        hidden_dim: int = 256,
        clip_range: float = 0.2,
        clip_range_vf: float = 0.2,
        vf_coef: float = 0.5,
        ent_coef: float = 0.01,
        aug_coef: float = 0.1,
        max_grad_norm: float = 0.5,
        policy_epochs: int = 32,
        aux_epochs: int = 6,
        kl_coef: float = 1.0,
        num_aux_mini_batch: int = 4,
        num_aux_grad_accum: int = 1,
        network_init_method: str = "xavier_uniform",
    ) -> None:
        super().__init__(observation_space, action_space, device, feature_dim, lr, eps)

        self.clip_range = clip_range
        self.clip_range_vf = clip_range_vf
        self.vf_coef = vf_coef
        self.ent_coef = ent_coef
        self.aug_coef = aug_coef
        self.max_grad_norm = max_grad_norm
        self.policy_epochs = policy_epochs
        self.aux_epochs = aux_epochs
        self.kl_coef = kl_coef
        self.num_aux_grad_accum = num_aux_grad_accum
        self.num_aux_mini_batch = num_aux_mini_batch
        self.network_init_method = network_init_method

        # auxiliary storage
        self.aux_obs = None
        self.aux_returns = None
        # self.aux_logits = None
        self.aux_policy_outputs = None

        # create models
        self.encoder = None
        # create models
        self.ac = OnPolicySharedActorCritic(
            obs_shape=self.obs_shape,
            action_dim=self.action_dim,
            action_type=self.action_type,
            feature_dim=feature_dim,
            hidden_dim=hidden_dim,
            aux_critic=True,
        )

    def train(self, training: bool = True) -> None:
        """Set the train mode.

        Args:
            training (bool): True (training) or False (testing).

        Returns:
            None.
        """
        self.training = training
        self.ac.train(training)

    def integrate(self, **kwargs) -> None:
        """Integrate agent and other modules (encoder, reward, ...) together"""
        # set encoder and distribution
        self.dist = kwargs["dist"]
        self.ac.encoder = kwargs["encoder"]
        self.ac.dist = kwargs["dist"]
        # network initialization
        self.ac.apply(get_network_init(self.network_init_method))
        # to device
        self.ac.to(self.device)
        # create optimizers
        self.ac_opt = th.optim.Adam(self.ac.parameters(), lr=self.lr, eps=self.eps)
        # set training mode
        self.train()
        # set augmentation and intrinsic reward
        if kwargs["aug"] is not None:
            self.aug = kwargs["aug"]
        if kwargs["irs"] is not None:
            self.irs = kwargs["irs"]

    def get_value(self, obs: th.Tensor) -> th.Tensor:
        """Get estimated values for observations.

        Args:
            obs (Tensor): Observations.

        Returns:
            Estimated values.
        """
        return self.ac.get_value(obs)

    def act(self, obs: th.Tensor, training: bool = True, step: int = 0) -> Union[Tuple[th.Tensor, ...], Dict[str, Any]]:
        """Sample actions based on observations.

        Args:
            obs: Observations.
            training: training mode, True or False.
            step: Global training step.

        Returns:
            Sampled actions.
        """
        if training:
            actions, values, log_probs = self.ac.get_action_and_value(obs)
            return {"actions": actions, "values": values, "log_probs": log_probs}
        else:
            actions = self.ac.get_det_action(obs)
            return actions

    def update(self, rollout_storage: Storage, episode: int = 0) -> Dict[str, float]:  # noqa: c901
        """Update the agent.

        Args:
            rollout_storage (Storage): Hsuanwu rollout storage.
            episode (int): Global training episode.

        Returns:
            Training metrics such as actor loss, critic_loss, etc.
        """

        # TODO: Save auxiliary transitions
        if episode == 0:
            num_steps, num_envs = rollout_storage.actions.size()[:2]
            self.aux_obs = th.empty(
                size=(
                    num_steps,
                    num_envs * self.policy_epochs,
                    *self.obs_shape,
                ),
                device="cpu",
                dtype=th.float32,
            )
            self.aux_returns = th.empty(
                size=(num_steps, num_envs * self.policy_epochs),
                device="cpu",
                dtype=th.float32,
            )
            if self.action_type == "Discrete":
                self.aux_policy_outputs = th.empty(
                    size=(
                        num_steps,
                        num_envs * self.policy_epochs,
                        self.action_dim,
                    ),
                    device="cpu",
                    dtype=th.float32,
                )
            elif self.action_type == "Box":
                self.aux_policy_outputs = th.empty(
                    size=(
                        num_steps,
                        num_envs * self.policy_epochs,
                        self.action_shape[0] * 2,
                    ),
                    device="cpu",
                    dtype=th.float32,
                )
            else:
                raise NotImplementedError
            self.num_aux_rollouts = num_envs * self.policy_epochs
            self.num_envs = num_envs
            self.num_steps = num_steps

        idx = int(episode % self.policy_epochs)
        self.aux_obs[:, idx * self.num_envs : (idx + 1) * self.num_envs].copy_(rollout_storage.obs[:-1].clone())
        self.aux_returns[:, idx * self.num_envs : (idx + 1) * self.num_envs].copy_(rollout_storage.returns.clone())

        # TODO: Policy phase
        total_actor_loss = []
        total_critic_loss = []
        total_entropy_loss = []
        total_aug_loss = []

        generator = rollout_storage.sample()

        if self.irs is not None:
            intrinsic_reward = self.irs.compute_irs(
                samples={
                    "obs": rollout_storage.obs[:-1],
                    "actions": rollout_storage.actions,
                    "next_obs": rollout_storage.obs[1:],
                },
                step=episode * self.num_envs * self.num_steps,
            )
            rollout_storage.rewards += intrinsic_reward.to(self.device)

        for batch in generator:
            (
                batch_obs,
                batch_actions,
                batch_values,
                batch_returns,
                batch_terminateds,
                batch_truncateds,
                batch_old_log_probs,
                adv_targ,
            ) = batch

            # evaluate sampled actions
            new_values, new_log_probs, entropy = self.ac.evaluate_actions(obs=batch_obs, actions=batch_actions)

            # actor loss part
            ratio = th.exp(new_log_probs - batch_old_log_probs)
            surr1 = ratio * adv_targ
            surr2 = th.clamp(ratio, 1.0 - self.clip_range, 1.0 + self.clip_range) * adv_targ
            actor_loss = -th.min(surr1, surr2).mean()

            # critic loss part
            if self.clip_range_vf is None:
                critic_loss = 0.5 * (new_values.flatten() - batch_returns).pow(2).mean()
            else:
                values_clipped = batch_values + (new_values.flatten() - batch_values).clamp(
                    -self.clip_range_vf, self.clip_range_vf
                )
                values_losses = (new_values.flatten() - batch_returns).pow(2)
                values_losses_clipped = (values_clipped - batch_returns).pow(2)
                critic_loss = 0.5 * th.max(values_losses, values_losses_clipped).mean()

            if self.aug is not None:
                # augmentation loss part
                batch_obs_aug = self.aug(batch_obs)
                new_batch_actions, _, _ = self.ac.get_action_and_value(obs=batch_obs)

                values_aug, log_probs_aug, _ = self.ac.evaluate_actions(obs=batch_obs_aug, actions=new_batch_actions)
                action_loss_aug = -log_probs_aug.mean()
                value_loss_aug = 0.5 * (th.detach(new_values) - values_aug).pow(2).mean()
                aug_loss = self.aug_coef * (action_loss_aug + value_loss_aug)
            else:
                aug_loss = th.scalar_tensor(s=0.0, requires_grad=False, device=critic_loss.device)

            # update
            self.ac_opt.zero_grad(set_to_none=True)
            loss = critic_loss * self.vf_coef + actor_loss - entropy * self.ent_coef + aug_loss
            loss.backward()
            nn.utils.clip_grad_norm_(self.ac.parameters(), self.max_grad_norm)
            self.ac_opt.step()

            total_actor_loss.append(actor_loss.item())
            total_critic_loss.append(critic_loss.item())
            total_entropy_loss.append(entropy.item())
            total_aug_loss.append(aug_loss.item())

        if (episode + 1) % self.policy_epochs != 0:
            # if not auxiliary phase, return train loss directly.
            return {
                "actor_loss": np.mean(total_actor_loss),
                "critic_loss": np.mean(total_critic_loss),
                "entropy_loss": np.mean(total_entropy_loss),
            }

        # TODO: Auxiliary phase
        for idx in range(self.policy_epochs):
            with th.no_grad():
                aux_obs = (
                    self.aux_obs[:, idx * self.num_envs : (idx + 1) * self.num_envs]
                    .to(self.device)
                    .reshape(-1, *self.aux_obs.size()[2:])
                )
                # get policy outputs
                policy_outputs = self.ac.get_policy_outputs(aux_obs).cpu().clone()
                self.aux_policy_outputs[:, idx * self.num_envs : (idx + 1) * self.num_envs] = policy_outputs.reshape(
                    self.num_steps, self.num_envs, self.aux_policy_outputs.size()[2]
                )

        total_aux_value_loss = []
        total_kl_loss = []

        for _e in range(self.aux_epochs):
            aux_inds = np.arange(self.num_aux_rollouts)
            np.random.shuffle(aux_inds)

            for idx in range(0, self.num_aux_rollouts, self.num_aux_mini_batch):
                batch_inds = aux_inds[idx : idx + self.num_aux_mini_batch]
                batch_aux_obs = self.aux_obs[:, batch_inds].reshape(-1, *self.aux_obs.size()[2:]).to(self.device)
                batch_aux_returns = self.aux_returns[:, batch_inds].reshape(-1, *self.aux_returns.size()[2:]).to(self.device)
                # batch_aux_logits = self.aux_logits[:, batch_inds].reshape(-1, *self.aux_logits.size()[2:]).to(self.device)
                batch_aux_policy_outputs = (
                    self.aux_policy_outputs[:, batch_inds].reshape(-1, *self.aux_policy_outputs.size()[2:]).to(self.device)
                )

                new_dist, new_values, new_aux_values = self.ac.get_dist_and_aux_value(batch_aux_obs)

                new_values = new_values.view(-1)
                new_aux_values = new_aux_values.view(-1)
                if self.action_type == "Discrete":
                    old_dist = self.dist(batch_aux_policy_outputs)
                elif self.action_type == "Box":
                    old_dist = self.dist(*batch_aux_policy_outputs.chunk(2, dim=1))
                else:
                    raise NotImplementedError
                # divergence loss
                kl_loss = th.distributions.kl_divergence(old_dist, new_dist).mean()
                # value loss
                value_loss = 0.5 * (new_values - batch_aux_returns).mean()
                aux_value_loss = 0.5 * (new_aux_values - batch_aux_returns).mean()
                # total loss
                (value_loss + aux_value_loss + self.kl_coef * kl_loss).backward()

                if (idx + 1) % self.num_aux_grad_accum == 0:
                    self.ac_opt.zero_grad(set_to_none=True)
                    nn.utils.clip_grad_norm_(self.ac.parameters(), self.max_grad_norm)
                    self.ac_opt.step()

                total_aux_value_loss.append(value_loss.item())
                total_aux_value_loss.append(aux_value_loss.item())
                total_kl_loss.append(kl_loss.item())

        return {"aux_value_loss": np.mean(total_aux_value_loss), "kl_loss": np.mean(total_kl_loss)}

    def save(self, path: Path) -> None:
        """Save models.

        Args:
            path (Path): Storage path.

        Returns:
            None.
        """
        if "pretrained" in str(path):  # pretraining
            th.save(self.ac.state_dict(), path / "actor_critic.pth")
        else:
            del self.ac.critic, self.ac.aux_critic, self.ac.dist
            th.save(self.ac, path / "agent.pth")

    def load(self, path: str) -> None:
        """Load initial parameters.

        Args:
            path (str): Import path.

        Returns:
            None.
        """
        actor_critic_params = th.load(os.path.join(path, "actor_critic.pth"), map_location=self.device)
        self.ac.load_state_dict(actor_critic_params)
