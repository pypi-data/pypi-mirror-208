# (generated with --quick)

import hsuanwu.xplore.augmentation.base
import torch as th
from typing import Any, Type

BaseAugmentation: Type[hsuanwu.xplore.augmentation.base.BaseAugmentation]

class RandomCutoutColor(hsuanwu.xplore.augmentation.base.BaseAugmentation):
    __doc__: str
    max_cut: int
    min_cut: int
    def __init__(self, min_cut: int = ..., max_cut: int = ...) -> None: ...
    def forward(self, x) -> Any: ...
