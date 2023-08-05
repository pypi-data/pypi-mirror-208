# (generated with --quick)

import cv2
import numpy as np
import random
import skvideo
import tqdm
from typing import Any

class BackgroundMatting:
    __doc__: str
    _color: Any
    def __init__(self, color) -> None: ...
    def get_mask(self, img) -> Any: ...

class FixedColorSource(ImageSource):
    arr: Any
    def __init__(self, shape, color) -> None: ...
    def get_image(self) -> Any: ...

class ImageSource:
    __doc__: str
    def get_image(self) -> None: ...
    def reset(self) -> None: ...

class NoiseSource(ImageSource):
    shape: Any
    strength: Any
    def __init__(self, shape, strength = ...) -> None: ...
    def get_image(self) -> Any: ...

class RandomColorSource(ImageSource):
    _color: Any
    arr: Any
    shape: Any
    def __init__(self, shape) -> None: ...
    def get_image(self) -> Any: ...
    def reset(self) -> None: ...

class RandomImageSource(ImageSource):
    _loc: Any
    arr: Any
    current_idx: int
    filelist: Any
    grayscale: Any
    shape: Any
    total_frames: Any
    def __init__(self, shape, filelist, total_frames = ..., grayscale = ...) -> None: ...
    def build_arr(self) -> None: ...
    def get_image(self) -> Any: ...
    def reset(self) -> None: ...

class RandomVideoSource(ImageSource):
    _loc: Any
    arr: Any
    current_idx: int
    filelist: Any
    grayscale: Any
    shape: Any
    total_frames: Any
    def __init__(self, shape, filelist, total_frames = ..., grayscale = ...) -> None: ...
    def build_arr(self) -> None: ...
    def get_image(self) -> Any: ...
    def reset(self) -> None: ...
