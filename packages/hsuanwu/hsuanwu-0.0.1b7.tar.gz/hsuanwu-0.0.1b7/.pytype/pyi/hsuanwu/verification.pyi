# (generated with --quick)

import gymnasium as gym
import hsuanwu.common.engine
import hsuanwu.env.utils
from typing import Any, Callable, Iterable, Optional, Type

HsuanwuEngine: Type[hsuanwu.common.engine.HsuanwuEngine]
HsuanwuEnvWrapper: Type[hsuanwu.env.utils.HsuanwuEnvWrapper]
OmegaConf: Any
cfgs: Any
engine: hsuanwu.common.engine.HsuanwuEngine
train_env: hsuanwu.env.utils.HsuanwuEnvWrapper

def colored(text: str, color: Optional[str] = ..., on_color: Optional[str] = ..., attrs: Optional[Iterable[str]] = ...) -> str: ...
def make_env() -> Callable[[], Any]: ...
