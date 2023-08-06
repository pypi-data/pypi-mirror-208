# (generated with --quick)

import hsuanwu.xplore.augmentation.base
import torch as th
from torchvision import transforms as T
from typing import Any, Type

BaseAugmentation: Type[hsuanwu.xplore.augmentation.base.BaseAugmentation]

class RandomAugment(hsuanwu.xplore.augmentation.base.BaseAugmentation):
    __doc__: str
    auto_augment_function: Any
    def __init__(self) -> None: ...
    def forward(self, x) -> Any: ...
