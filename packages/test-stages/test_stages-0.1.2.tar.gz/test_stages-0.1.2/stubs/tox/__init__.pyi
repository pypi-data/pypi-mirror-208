# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

from collections.abc import Callable
from typing import TypeVar

import tox.config


TParserHook = Callable[[tox.config.Parser], None]


# This only handles the parser hook right now.
def hookimpl(func: TParserHook) -> TParserHook: ...
