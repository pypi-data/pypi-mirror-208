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
from typing import Optional

from .locations import Location, TimezoneInfo


@dataclass
class SleepTimeSettings:
    """Represents a setting for sleep time from a user setting.

    .. versionadded:: 1.5.0
    """

    enabled: bool
    end_time: Optional[int]
    start_time: Optional[int]


@dataclass
class UserSettings:
    """Represents a user setting.

    .. versionadded:: 1.5.0
    """

    always_use_https: Optional[bool]
    geo_enabled: Optional[bool]
    sleep_time_setting: SleepTimeSettings
    use_cookie_personalization: Optional[bool]
    language: Optional[str]
    discoverable_by_email: Optional[bool]
    discoverable_by_mobile_phone: Optional[bool]
    display_sensitive_media: Optional[bool]
    allow_contributor_request: Optional[str]
    allow_dms_from: Optional[str]
    allow_dm_groups_from: Optional[str]
    protected: Optional[bool]
    translator_type: Optional[str]
    screen_name: Optional[str]
    show_all_inline_media: Optional[bool] = None
    location: Optional[Location] = None
    timezone: Optional[TimezoneInfo] = None
