# (generated with --quick)

import hsuanwu.xplore.augmentation.base
import torch as th
from torchvision import transforms as T
from typing import Any, Type

BaseAugmentation: Type[hsuanwu.xplore.augmentation.base.BaseAugmentation]

class AutoAugment(hsuanwu.xplore.augmentation.base.BaseAugmentation):
    __doc__: str
    auto_augment_function: Any
    policy: str
    def __init__(self, augment_policy: str = ...) -> None: ...
    def forward(self, x) -> Any: ...
