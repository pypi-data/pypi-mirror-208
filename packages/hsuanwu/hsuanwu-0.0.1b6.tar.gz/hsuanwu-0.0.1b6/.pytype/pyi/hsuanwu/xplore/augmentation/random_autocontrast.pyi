# (generated with --quick)

import hsuanwu.xplore.augmentation.base
import torch as th
from torchvision import transforms as T
from typing import Any, Type

BaseAugmentation: Type[hsuanwu.xplore.augmentation.base.BaseAugmentation]

class RandomAutocontrast(hsuanwu.xplore.augmentation.base.BaseAugmentation):
    __doc__: str
    augment_function: Any
    p: float
    def __init__(self, p: float = ...) -> None: ...
    def forward(self, x) -> Any: ...
