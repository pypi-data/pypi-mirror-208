# (generated with --quick)

import hsuanwu.xplore.augmentation.base
import torch as th
from torchvision import transforms as T
from typing import Any, Type

BaseAugmentation: Type[hsuanwu.xplore.augmentation.base.BaseAugmentation]

class RandomPerspective(hsuanwu.xplore.augmentation.base.BaseAugmentation):
    __doc__: str
    augment_function: Any
    distortion_scale: float
    fill: Any
    interpolation: int
    p: float
    def __init__(self, distortion_scale: float = ..., p: float = ..., interpolation: int = ..., fill = ...) -> None: ...
    def forward(self, x) -> Any: ...
