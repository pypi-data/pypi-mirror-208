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

import random
import string
import threading
from concurrent.futures import ThreadPoolExecutor, wait
from typing import Any, Callable, Optional

from ..constants import ALL_COMPLETED

__all__ = ("Executor", "ThreadManager")


class Executor(ThreadPoolExecutor):
    def __init__(self, *args, **kwargs):
        self._session_id = kwargs.pop("session_id")
        self._thread_name = kwargs.pop("thread_name")
        self._futures = []
        self._thread_name += f":session_id={self.session_id}:task_number="
        super().__init__(thread_name_prefix=self._thread_name, *args, **kwargs)

    @property
    def futures(self):
        return self._futures

    @property
    def threads(self):
        return self._threads

    @property
    def session_id(self):
        return self._session_id

    def submit(self, fn: Callable, *args: Any, **kwargs: Any):
        future = super().submit(fn, *args, **kwargs)
        self.futures.append(future)
        return future

    def clear_futures(self):
        self.futures.clear()

    def wait_for_futures(
        self,
        *,
        timeout: Optional[int] = None,
        return_when=ALL_COMPLETED,
        purge: bool = True,
    ):
        if not self.futures:
            return None
        result = wait(self.futures, timeout, return_when)
        if purge:
            self.clear_futures()
        return result


class ThreadManager:
    @property
    def active_threads(self) -> list:
        return threading.enumerate()

    def create_new_executor(self, *, max_workers: int = 100, thread_name: str = "", session_id: str = None) -> Executor:
        return Executor(
            max_workers,
            thread_name=thread_name,
            session_id=session_id or self.generate_thread_session(),
        )

    def get_threads(self, session_id):
        threads = []
        for t in self.active_threads:
            if session_id in t.name:
                threads.append(t)
        return threads

    def generate_thread_session(self):
        return "".join((random.sample(string.ascii_lowercase, 10)))
