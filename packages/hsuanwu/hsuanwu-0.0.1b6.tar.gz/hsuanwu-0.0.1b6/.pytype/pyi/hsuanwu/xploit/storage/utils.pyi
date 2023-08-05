# (generated with --quick)

import io
import numpy as np
import pathlib
import random
from typing import Type

Path: Type[pathlib.Path]

def dump_episode(episode: dict, fn: pathlib.Path) -> None: ...
def episode_len(episode: dict) -> int: ...
def load_episode(fn: pathlib.Path) -> dict: ...
def worker_init_fn(worker_id) -> None: ...
