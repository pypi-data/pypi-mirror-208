"""
pytwot
~~~~~~~

pytwot is a Synchronous python API wrapper for Twitter's API!

:copyright: (c) 2021-present UnrealFar & TheGenocides, 2023-present Sengolda
:license: MIT, see LICENSE for more details.
"""
import logging
from typing import Literal, NamedTuple

from .attachments import *
from .auth import *
from .client import *
from .compliance import *
from .constants import *
from .dataclass import *
from .entities import *
from .enums import *
from .environment import *
from .errors import *
from .events import *
from .http import *
from .list import *
from .message import *
from .objects import *
from .paginations import *
from .parser import *
from .relations import *
from .space import *
from .stream import *
from .tweet import *
from .user import *
from .utils import *

__title__ = "pytwot"
__author__ = "Sengolda"
__version__ = "1.5.1"
__license__ = "MIT"
__copyright__ = "Copyright 2021-present UnrealFar & TheGenocides, 2023-present Sengolda"


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info: VersionInfo = VersionInfo(major=1, minor=5, micro=1, releaselevel="final", serial=1)


logging.getLogger(__name__).addHandler(logging.NullHandler())

assert version_info.releaselevel in (
    "alpha",
    "beta",
    "candidate",
    "final",
), "Invalid release level given."
