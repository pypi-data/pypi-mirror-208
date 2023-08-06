# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

from collections.abc import Iterable
from typing import Any, Dict, List


class Parser:
    def add_testenv_attribute(
        self,
        name: str,
        type: str,
        help: str,
        default: Any = None,
        postprocess: Any = None,
    ) -> None: ...


class TestenvConfig:
    tags: List[str]


class Config:
    envconfigs: Dict[str, TestenvConfig]


def parseconfig(args: List[str], plugins: Iterable[str] = ()) -> Config: ...
