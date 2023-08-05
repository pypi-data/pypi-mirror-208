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
from typing import Union, Optional
from ..enums import ButtonType


@dataclass
class Option:
    """Represents an Option object for :class:`QuickReply`. You can add an Option using :meth:`QuickReply.add_option`.

    .. versionadded:: 1.3.5
    """

    label: str
    description: str
    metadata: str


@dataclass
class PollOption:
    """Represents an Option for :class:`Poll`. You can add an option to a poll using :meth:`Poll.add_option`.

    .. versionadded:: 1.3.5
    """

    label: str
    position: int = 0
    votes: int = 0


@dataclass
class Button:
    """Represents a Button object. Button is an attachment that you can attach via :meth:`CTA.add_button`.

    .. versionadded:: 1.3.5
    """

    label: str
    type: Union[ButtonType, str]
    url: str
    tco_url: Optional[str] = None
