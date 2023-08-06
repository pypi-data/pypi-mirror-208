# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

import pathlib


class BuildBackendHookCaller:
    def __init__(self, source_dir: pathlib.Path, build_backend: str) -> None: ...
    def build_sdist(self, distdir: pathlib.Path) -> str: ...
