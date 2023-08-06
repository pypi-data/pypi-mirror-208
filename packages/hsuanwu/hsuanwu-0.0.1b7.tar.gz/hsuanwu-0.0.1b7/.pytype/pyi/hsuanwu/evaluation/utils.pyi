# (generated with --quick)

import numpy as np
from arch import bootstrap as arch_bs
from numpy import random
from typing import Any, Dict, List, Tuple

Float = Any

class StratifiedBootstrap(Any):
    __doc__: str
    _args_shape: Tuple[int, ...]
    _name: str
    _num_tasks: int
    _parameters: List[int]
    _strata_indices: List[np.ndarray[Any, np.dtype]]
    _task_bootstrap: bool
    def __init__(self, *args: np.ndarray, random_state = ..., task_bootstrap: bool = ..., **kwargs: np.ndarray) -> None: ...
    def _get_strata_indices(self) -> List[np.ndarray]: ...
    def update_indices(self) -> Tuple[np.ndarray, ...]: ...

class StratifiedIndependentBootstrap(Any):
    __doc__: str
    _args_shapes: List[Tuple[int, ...]]
    _args_strata_indices: list
    _kwargs_shapes: dict
    _kwargs_strata_indices: dict
    def __init__(self, *args: np.ndarray, random_state = ..., **kwargs: np.ndarray) -> None: ...
    def _get_indices(self, num_runs: int, array_shape: Tuple[int, ...], strata_indices: List[np.ndarray]) -> Tuple[np.ndarray, ...]: ...
    def _get_strata_indices(self, array_shape: Tuple[int, ...]) -> List[np.ndarray]: ...
    def update_indices(self) -> Tuple[List[Tuple[np.ndarray, ...]], Dict[str, Tuple[np.ndarray, ...]]]: ...

def min_max_normalize(value: np.ndarray, min_scores: np.ndarray, max_scores: np.ndarray) -> np.ndarray: ...
