# (generated with --quick)

import hsuanwu.xplore.augmentation.base
import torch as th
from typing import Any, Type

BaseAugmentation: Type[hsuanwu.xplore.augmentation.base.BaseAugmentation]

class RandomTranslate(hsuanwu.xplore.augmentation.base.BaseAugmentation):
    __doc__: str
    scale_factor: float
    size: int
    def __init__(self, size: int = ..., scale_factor: float = ...) -> None: ...
    def forward(self, x) -> Any: ...
