# (generated with --quick)

import hsuanwu.xplore.augmentation.base
import torch as th
from typing import Any, Type

BaseAugmentation: Type[hsuanwu.xplore.augmentation.base.BaseAugmentation]
ColorJitter: Any

class RandomColorJitter(hsuanwu.xplore.augmentation.base.BaseAugmentation):
    __doc__: str
    color_jitter: Any
    def __init__(self, brightness: float = ..., contrast: float = ..., saturation: float = ..., hue: float = ...) -> None: ...
    def forward(self, x) -> Any: ...
