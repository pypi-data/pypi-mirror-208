# (generated with --quick)

import hsuanwu.xplore.augmentation.base
import torch as th
from typing import Any, Type

BaseAugmentation: Type[hsuanwu.xplore.augmentation.base.BaseAugmentation]
Uniform: Any

class RandomAmplitudeScaling(hsuanwu.xplore.augmentation.base.BaseAugmentation):
    __doc__: str
    dist: Any
    def __init__(self, low: float = ..., high: float = ...) -> None: ...
    def forward(self, x) -> Any: ...
