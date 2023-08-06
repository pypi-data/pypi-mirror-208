# (generated with --quick)

import hsuanwu.xplore.augmentation.base
import torch as th
from typing import Any, Type

BaseAugmentation: Type[hsuanwu.xplore.augmentation.base.BaseAugmentation]

class RandomRotate(hsuanwu.xplore.augmentation.base.BaseAugmentation):
    __doc__: str
    p: float
    def __init__(self, p: float = ...) -> None: ...
    def forward(self, x) -> Any: ...
