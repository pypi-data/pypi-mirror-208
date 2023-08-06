#  Copyright 2023 MTS (Mobile Telesystems)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from functools import wraps
from typing import Callable, NoReturn, Type

from evacuator.exception import NeedEvacuation

logger = logging.getLogger(__name__)

ECANCELED = 125


def evacuator(
    func: Callable | None = None,
    exception: Type[Exception] | tuple[Type[Exception], ...] = NeedEvacuation,
    exit_code: int = ECANCELED,
):
    """Catch specific exception and exit with exit code.

    Can be used as either decorator or context manager

    Parameters
    -----------

    func : Callable

        Function which should we wrapped with a decorator

    exception : Exception | tuple[Exception, ...], default :obj:`evacuator.exception.NeedEvacuation`

        Exception or exceptions which should be caught

    exit_code : int, default ``125`` (Unix ``ECANCELED``)

        Code which process should be exited with

    Examples
    --------

    Decorator example

    .. code:: python

        from evacuator import evacuator


        @evacuator
        def main():
            raise NeedEvacuation("abc")


        @evacuator(exception=(MyException, RuntimeError))
        def main():
            raise MyException("abc")


        @evacuator(exception=MyException, exit_code=5)
        def main():
            raise MyException("abc")

    Context manager example

    .. code:: python

        from evacuator import evacuator

        with evacuator():
            raise NeedEvacuation("abc")

        with evacuator(exception=(MyException, RuntimeError)):
            raise MyException("abc")

        with evacuator(exception=MyException, exit_code=5):
            raise MyException("abc")
    """

    if func:
        return DieContext(exception=exception, exit_code=exit_code)(func)

    return DieContext(exception=exception, exit_code=exit_code)


@dataclass(frozen=True)
class DieContext:
    """Catch specific exception and exit with exit code"""

    exception: Type[Exception] | tuple[Type[Exception], ...] = NeedEvacuation
    exit_code: int = ECANCELED

    def __call__(self, func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except self.exception:
                self._handle()

        return wrapper

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, _traceback):
        if exc_type is not None and issubclass(exc_type, self.exception):
            self._handle()

    def _handle(self) -> NoReturn:
        logger.exception("Caught an exception")
        logger.exception("Die with exit code %s", self.exit_code, exc_info=False)
        sys.exit(self.exit_code)
