# (generated with --quick)

import hsuanwu.xplore.augmentation.base
import torch as th
from torch.nn import functional as F
from typing import Any, Type

BaseAugmentation: Type[hsuanwu.xplore.augmentation.base.BaseAugmentation]

class RandomShift(hsuanwu.xplore.augmentation.base.BaseAugmentation):
    __doc__: str
    _pad: int
    def __init__(self, pad: int = ...) -> None: ...
    def forward(self, x) -> Any: ...
