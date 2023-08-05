from .base import BaseIntrinsicRewardModule as BaseIntrinsicRewardModule
from .girm import GIRM as GIRM
from .icm import ICM as ICM
from .ngu import NGU as NGU
from .pseudo_counts import PseudoCounts as PseudoCounts
from .re3 import RE3 as RE3
from .revd import REVD as REVD
from .ride import RIDE as RIDE
from .rise import RISE as RISE
from .rnd import RND as RND

ALL_IRS_MODULES = [
    "BaseIntrinsicRewardModule",
    "PseudoCounts",
    "GIRM",
    "ICM",
    "NGU",
    "RE3",
    "REVD",
    "RIDE",
    "RISE",
    "RND",
]
