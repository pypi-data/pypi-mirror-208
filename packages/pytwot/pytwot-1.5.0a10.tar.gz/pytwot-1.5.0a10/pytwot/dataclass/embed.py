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

from dataclasses import dataclass
from typing import List, Optional

__all__ = ("Embed", "EmbedImage")


@dataclass
class EmbedImage:
    """Represents a dataclass for an embed image.

    .. versionadded: 1.1.3

    .. versionchanged: 1.5.0

        Made as a dataclass rather then a standalone class.
    """

    url: str
    width: int
    height: int


@dataclass
class Embed:
    """Represents a dataclass for embedded urls in a tweet.

    .. versionadded: 1.1.3


    .. versionchanged: 1.5.0

        Made as a dataclass rather then a standalone class.
    """

    title: Optional[str] = None
    description: Optional[str] = None
    start: Optional[int] = None
    end: Optional[int] = None
    url: Optional[str] = None
    expanded_url: Optional[str] = None
    display_url: Optional[str] = None
    unwound_url: Optional[str] = None
    status_code: Optional[int] = None
    images: Optional[List[EmbedImage]] = None
