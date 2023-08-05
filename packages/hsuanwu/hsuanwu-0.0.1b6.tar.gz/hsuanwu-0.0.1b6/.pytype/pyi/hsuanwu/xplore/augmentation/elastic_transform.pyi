# (generated with --quick)

import hsuanwu.xplore.augmentation.base
import torch as th
from torchvision import transforms as T
from typing import Any, Type

BaseAugmentation: Type[hsuanwu.xplore.augmentation.base.BaseAugmentation]

class ElasticTransform(hsuanwu.xplore.augmentation.base.BaseAugmentation):
    __doc__: str
    alpha: float
    augment_function: Any
    fill: Any
    interpolation: int
    sigma: float
    def __init__(self, alpha: float = ..., sigma: float = ..., interpolation: int = ..., fill = ...) -> None: ...
    def forward(self, x) -> Any: ...
