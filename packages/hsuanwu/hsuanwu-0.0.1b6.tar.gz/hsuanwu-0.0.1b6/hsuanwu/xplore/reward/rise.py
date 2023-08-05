from typing import Dict, Tuple, Union

import gymnasium as gym
import numpy as np
import torch as th
from omegaconf import DictConfig
from torch import nn

from hsuanwu.xplore.reward.base import BaseIntrinsicRewardModule


class Encoder(nn.Module):
    """Encoder for encoding observations.

    Args:
        obs_shape (Tuple): The data shape of observations.
        action_dim (int): The dimension of actions.
        latent_dim (int): The dimension of encoding vectors.

    Returns:
        Encoder instance.
    """

    def __init__(self, obs_shape: Tuple, action_dim: int, latent_dim: int) -> None:
        super().__init__()

        # visual
        if len(obs_shape) == 3:
            self.trunk = nn.Sequential(
                nn.Conv2d(obs_shape[0], 32, 8, 4),
                nn.ReLU(),
                nn.Conv2d(32, 64, 4, 2),
                nn.ReLU(),
                nn.Conv2d(64, 64, 3, 1),
                nn.ReLU(),
                nn.Flatten(),
            )
            with th.no_grad():
                sample = th.ones(size=tuple(obs_shape))
                n_flatten = self.trunk(sample.unsqueeze(0)).shape[1]

            self.linear = nn.Linear(n_flatten, latent_dim)
        else:
            self.trunk = nn.Sequential(nn.Linear(obs_shape[0], 256), nn.ReLU())
            self.linear = nn.Linear(256, latent_dim)

    def forward(self, obs: th.Tensor) -> th.Tensor:
        """Encode the input tensors.

        Args:
            obs (Tensor): Observations.

        Returns:
            Encoding tensors.
        """
        return self.linear(self.trunk(obs))


class RISE(BaseIntrinsicRewardModule):
    """Rényi State Entropy Maximization for Exploration Acceleration in Reinforcement Learning (RISE).
        See paper: https://ieeexplore.ieee.org/abstract/document/9802917/

    Args:
        observation_space (Space or DictConfig): The observation space of environment. When invoked by Hydra,
            'observation_space' is a 'DictConfig' like {"shape": observation_space.shape, }.
        action_space (Space or DictConfig): The action space of environment. When invoked by Hydra,
            'action_space' is a 'DictConfig' like
            {"shape": action_space.shape, "n": action_space.n, "type": "Discrete", "range": [0, n - 1]} or
            {"shape": action_space.shape, "type": "Box", "range": [action_space.low[0], action_space.high[0]]}.
        device (str): Device (cpu, cuda, ...) on which the code should be run.
        beta (float): The initial weighting coefficient of the intrinsic rewards.
        kappa (float): The decay rate.
        latent_dim (int): The dimension of encoding vectors.
        alpha (alpha): The The order of Rényi entropy.
        k (int): Use the k-th neighbors.
        average_entropy (bool): Use the average of entropy estimation.

    Returns:
        Instance of RISE.
    """

    def __init__(
        self,
        observation_space: Union[gym.Space, DictConfig],
        action_space: Union[gym.Space, DictConfig],
        device: str = "cpu",
        beta: float = 0.05,
        kappa: float = 0.000025,
        latent_dim: int = 128,
        alpha: float = 0.5,
        k: int = 5,
        average_entropy: bool = False,
    ) -> None:
        super().__init__(observation_space, action_space, device, beta, kappa)
        self.random_encoder = Encoder(
            obs_shape=self._obs_shape,
            action_dim=self._action_dim,
            latent_dim=latent_dim,
        ).to(self._device)

        # freeze the network parameters
        for p in self.random_encoder.parameters():
            p.requires_grad = False

        self.alpha = alpha
        self.k = k
        self.average_entropy = average_entropy

    def compute_irs(self, samples: Dict, step: int = 0) -> th.Tensor:
        """Compute the intrinsic rewards for current samples.

        Args:
            samples (Dict): The collected samples. A python dict like
                {obs (n_steps, n_envs, *obs_shape) <class 'th.Tensor'>,
                actions (n_steps, n_envs, *action_shape) <class 'th.Tensor'>,
                rewards (n_steps, n_envs) <class 'th.Tensor'>,
                next_obs (n_steps, n_envs, *obs_shape) <class 'th.Tensor'>}.
            step (int): The global training step.

        Returns:
            The intrinsic rewards.
        """
        # compute the weighting coefficient of timestep t
        beta_t = self._beta * np.power(1.0 - self._kappa, step)
        num_steps = samples["obs"].size()[0]
        num_envs = samples["obs"].size()[1]
        obs_tensor = samples["obs"].to(self._device)

        intrinsic_rewards = th.zeros(size=(num_steps, num_envs)).to(self._device)

        with th.no_grad():
            for i in range(num_envs):
                src_feats = self.random_encoder(obs_tensor[:, i])
                dist = th.linalg.vector_norm(src_feats.unsqueeze(1) - src_feats, ord=2, dim=2)
                if self.average_entropy:
                    for sub_k in range(self.k):
                        intrinsic_rewards[:, i] += th.pow(th.kthvalue(dist, sub_k + 1, dim=1).values, 1.0 - self.alpha)

                    intrinsic_rewards[:, i] /= self.k
                else:
                    intrinsic_rewards[:, i] = th.pow(th.kthvalue(dist, self.k + 1, dim=1).values, 1.0 - self.alpha)

        return beta_t * intrinsic_rewards

    def update(self, samples: Dict) -> None:
        """Update the intrinsic reward module if necessary.

        Args:
            samples: The collected samples. A python dict like
                {obs (n_steps, n_envs, *obs_shape) <class 'th.Tensor'>,
                actions (n_steps, n_envs, *action_shape) <class 'th.Tensor'>,
                rewards (n_steps, n_envs) <class 'th.Tensor'>,
                next_obs (n_steps, n_envs, *obs_shape) <class 'th.Tensor'>}.

        Returns:
            None
        """
