# (generated with --quick)

import hsuanwu.evaluation.utils
import numpy as np
from numpy import random
from scipy import stats as sts
from typing import Any, Callable, Dict, Tuple, Type

StratifiedIndependentBootstrap: Type[hsuanwu.evaluation.utils.StratifiedIndependentBootstrap]

class Comparison:
    __doc__: str
    confidence_interval_size: float
    get_ci: bool
    method: str
    random_state: Any
    reps: int
    scores_x: np.ndarray[Any, np.dtype]
    scores_y: np.ndarray[Any, np.dtype]
    def __init__(self, scores_x: np.ndarray, scores_y: np.ndarray, get_ci: bool = ..., method: str = ..., reps: int = ..., confidence_interval_size: float = ..., random_state = ...) -> None: ...
    def compute_poi(self) -> Any: ...
    def get_interval_estimates(self, scores_x: np.ndarray, scores_y: np.ndarray, metric: Callable) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]: ...
