# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Load the Tox configuration, look for our tags thing."""

from __future__ import annotations

import contextlib
import pathlib
import shutil
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING

import pytest
import utf8_locale

import tox_trivtags
import tox_trivtags.parse as ttt_parse


if sys.version_info >= (3, 11):
    import contextlib as contextlib_chdir  # pylint: disable=reimported
else:
    import contextlib_chdir

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from contextlib import AbstractContextManager
    from typing import Final


_EXPECTED: Final[dict[str, list[str]]] = {
    "format": ["check"],
    "reformat": ["format", "manual"],
    "unit-tests-no-tox": ["tests"],
    "unit-tests-tox-3": ["tests"],
    "unit-tests-tox-4": ["tests"],
    (".package" if tox_trivtags.HAVE_MOD_TOX_3 else ".pkg"): [],
    "t-single": ["something"],
    "t-several": ["all", "the", "things"],
    "t-special": ["So,", "how many", "$tags", 'is "too many",', "'eh\"?"],
}


def copy_and_adapt(srcdir: pathlib.Path, dstdir: pathlib.Path) -> None:
    """Copy some files over, adapt the tox.ini file."""
    src_tox = srcdir / "tox.ini"
    dst_tox = dstdir / "tox.ini"
    lines: Final = src_tox.read_text(encoding="UTF-8").splitlines()
    adapted: Final = [
        line.replace(" \\", "") for line in lines if not line.startswith("minversion")
    ]
    dst_tox.write_text("".join(line + "\n" for line in adapted), encoding="UTF-8")
    res: Final = subprocess.run(["diff", "-u", "--", src_tox, dst_tox], check=False)
    assert res.returncode != 0

    shutil.copytree(srcdir / "config", dstdir / "config")
    shutil.copytree(srcdir / "requirements", dstdir / "requirements")
    shutil.copy2(srcdir / "pyproject.toml", dstdir / "pyproject.toml")


@contextlib.contextmanager
def adapt_tox_cwd() -> Iterator[pathlib.Path]:
    """If using Tox 3.x, copy the files over and adapt them."""
    cwd: Final = pathlib.Path("").absolute()
    if not tox_trivtags.HAVE_MOD_TOX_3:
        print("Not using Tox 3.x, no need to copy or adapt any files")
        yield cwd
        return

    with tempfile.TemporaryDirectory() as toxd_name:
        toxd = pathlib.Path(toxd_name).absolute()
        print(f"Adapting files for Tox 3.x from {cwd} to {toxd}")
        copy_and_adapt(cwd, toxd)
        with contextlib_chdir.chdir(toxd):
            yield toxd


@contextlib.contextmanager
def _cfg_filename_cwd() -> Iterator[pathlib.Path]:
    """No arguments, parse the tox.ini file in the current directory."""
    yield pathlib.Path("tox.ini")


@contextlib.contextmanager
def _cfg_filename_tempdir() -> Iterator[pathlib.Path]:
    """Create a temporary directory, enter it, pass `-c` with the original cwd."""
    cwd: Final = pathlib.Path("").absolute()
    with tempfile.TemporaryDirectory() as tempd:
        print(f"Temporary directory: {tempd}; current directory: {cwd}")
        with contextlib_chdir.chdir(tempd):
            yield cwd / "tox.ini"


def _do_test_run_showconfig(filename: pathlib.Path) -> None:
    """Parse the `tox --showconfig` output."""
    u8env: Final = utf8_locale.UTF8Detect().detect().env
    print(f"Using {u8env['LC_ALL']} as a UTF-8-capable locale")

    envs: Final = ttt_parse.parse_showconfig(filename, env=u8env)
    print(f"Got some Tox config sections: {' '.join(sorted(envs))}")
    for envname, expected in _EXPECTED.items():
        print(f"- envname {envname!r} expected {expected!r}")
        assert envs[envname].tags == expected


@pytest.mark.parametrize("cfg_filename", [_cfg_filename_cwd, _cfg_filename_tempdir])
def test_run_showconfig(cfg_filename: Callable[[], AbstractContextManager[pathlib.Path]]) -> None:
    """Run `tox --showconfig` expecting tox.ini to be in the specified directory."""
    print()
    with adapt_tox_cwd(), cfg_filename() as filename:
        _do_test_run_showconfig(filename)
