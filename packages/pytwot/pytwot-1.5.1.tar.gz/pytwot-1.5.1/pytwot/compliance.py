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

import datetime
import json
from typing import TYPE_CHECKING, List, Optional

import requests

from .dataclass import JobResult
from .enums import JobResultAction, JobResultActionReason, JobStatus, JobType
from .objects import Comparable
from .utils import time_parse_todt

if TYPE_CHECKING:
    from .http import HTTPClient
    from .type import ID, Payload


class Job(Comparable):
    """Represents a job compliance.

    .. versionadded:: 1.5.0
    """

    __slots__ = ("__payload", "http_client")

    def __init__(self, data: Payload, *, http_client: Optional[HTTPClient] = None):
        self.__payload = data
        self.http_client = http_client
        super().__init__(self.id)

    def __repr__(self):
        return f"Job(name={self.name} id={self.id} type={self.type})"

    @property
    def name(self) -> str:
        """:class:`str`: Returns the job's name

        .. versionadded:: 1.5.0
        """
        return self.__payload.get("name")

    @property
    def id(self) -> ID:
        """:class:`id`: Returns the job's id

        .. versionadded:: 1.5.0
        """
        return int(self.__payload.get("id"))

    @property
    def resumable(self) -> bool:
        """:class:`bool`: Returns True if the job is esumable otherwise False.

        .. versionadded:: 1.5.0
        """
        return self.__payload.get("resumable")

    @property
    def download_url(self) -> str:
        """:class:`str`: Returns the job's download url.

        .. versionadded:: 1.5.0
        """
        return self.__payload.get("download_url")

    @property
    def upload_url(self) -> str:
        """:class:`str`: Returns the job's upload url.

        .. versionadded:: 1.5.0
        """
        return self.__payload.get("upload_url")

    @property
    def type(self) -> JobType:
        """:class:`JobType`: Returns :class:`JobType` with the job's type.

        .. versionadded:: 1.5.0
        """
        return JobType(self.__payload.get("type"))

    @property
    def status(self) -> JobStatus:
        """:class:`JobStatus`: Returns :class:`JobStatus` with the job's status.

        .. versionadded:: 1.5.0
        """
        return JobStatus(self.__payload.get("status"))

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns a datetime.datetime object with the job's created timestamp.

        .. versionadded:: 1.5.0
        """
        return time_parse_todt(self.__payload.get("created_at"))

    @property
    def download_expires_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns a datetime.datetime object which the download URL will be available (usually seven days from the request time).

        .. versionadded:: 1.5.0
        """
        return time_parse_todt(self.__payload.get("download_expires_at"))

    @property
    def upload_expires_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns a datetime.datetime object which the upload URL will be available (usually seven days from the request time).

        .. versionadded:: 1.5.0
        """
        return time_parse_todt(self.__payload.get("upload_expires_at"))

    def upload_file(self, path_to_filename: str):
        """Upload a txt file to :meth:`Job.upload_url`.

        Parameters
        ------------
        path_to_filename: :class:`str`
            Path to the filename that you want to upload.


        .. versionadded:: 1.5.0
        """
        requests.put(self.upload_url, data=open(path_to_filename, "rb"), headers={"Content-Type": "text/plain"})

    def get_download_result(self) -> Optional[List[JobResult]]:
        """Get the download result of the job. You can only get the result if the job has a `complete` status, check :meth:`Job.status` to check the job's status.

        Returns
        ---------
        Optional[List[:class:`JobResult`]]
            This method returns a list of :class:`JobResult` objects.


        .. versionadded:: 1.5.0
        """
        res = requests.get(self.download_url)
        results = []
        for data in res.text.splitlines():
            if not data:
                return None

            if isinstance(data, str):
                data = json.loads(data)

            data["action"] = JobResultAction(data["action"])
            data["reason"] = JobResultActionReason(data["reason"])
            results.append(JobResult(**data))

        return results
