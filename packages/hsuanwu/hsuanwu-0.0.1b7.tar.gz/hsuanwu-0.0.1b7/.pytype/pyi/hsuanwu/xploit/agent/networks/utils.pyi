# (generated with --quick)

import torch as th
from torch import nn
from typing import Any, Callable

class ExportModel(Any):
    __doc__: str
    actor: Any
    encoder: Any
    def __init__(self, encoder, actor) -> None: ...
    def forward(self, obs) -> Any: ...

def get_network_init(method: str = ...) -> Callable: ...
