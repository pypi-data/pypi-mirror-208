"""
The MIT License (MIT)

Copyright (c) 2021-present UnrealFar & TheGenocides
Copyright (c) 2023-present Sengolda

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Location:
    """Represents a Location that Twitter has trending topic information for.

    .. versionadded:: 1.5.0
    """

    country: str
    country_code: str
    name: str
    parent_id: int
    place_type: PlaceType
    url: str
    woeid: int


@dataclass
class Trend:
    """Represents a twitter's trending topics display as Trend.

    .. versionadded:: 1.5.0
    """

    name: str
    url: str
    promoted_content: Optional[str]
    query: str
    tweet_volume: Optional[str]


@dataclass
class TimezoneInfo:
    """Represents a TimezoneInfo for the user's setting.

    .. versionadded:: 1.5.0
    """

    name: str
    name_info: str
    utc_offset: int


@dataclass
class PlaceType:
    """Represents a place type consist of the code and name for :class:`Location`.

    .. versionadded:: 1.5.0
    """

    code: int
    name: str
