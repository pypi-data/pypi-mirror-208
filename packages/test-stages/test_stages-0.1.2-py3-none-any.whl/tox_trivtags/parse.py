# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Query Tox for the tags defined in the specified file."""

# mypy needs these assertions, and they are better expressed in a compact manner

from __future__ import annotations

import ast
import configparser
import pathlib
import subprocess
import sys
from typing import Final, NamedTuple

from tox_trivtags import HAVE_MOD_TOX_3


DEFAULT_FILENAME = pathlib.Path("tox.ini")


class TestenvTags(NamedTuple):
    """A Tox environment along with its tags."""

    cfg_name: str
    name: str
    tags: list[str]


def _validate_parsed_bool(value: ast.expr) -> bool:
    """Make sure a boolean value is indeed a boolean value."""
    assert isinstance(value, ast.Constant) and isinstance(value.value, bool)
    return value.value


def _validate_parsed_str(value: ast.expr) -> str:
    """Make sure a string is indeed a string."""
    assert isinstance(value, ast.Constant) and isinstance(value.value, str)
    return value.value


def _validate_parsed_strlist(value: ast.expr) -> list[str]:
    """Make sure a list of strings is indeed a list of strings."""
    assert isinstance(value, ast.List)
    return [_validate_parsed_str(value) for value in value.elts]


def _parse_bool(value: str) -> bool:
    """Parse a Python-esque representation of a boolean value without eval()."""
    a_body: Final = ast.parse(value).body
    assert len(a_body) == 1 and isinstance(a_body[0], ast.Expr)
    return _validate_parsed_bool(a_body[0].value)


def _parse_strlist(value: str) -> list[str]:
    """Parse a Python-esque representation of a list of strings without eval()."""
    a_body: Final = ast.parse(value).body
    assert len(a_body) == 1 and isinstance(a_body[0], ast.Expr)
    return _validate_parsed_strlist(a_body[0].value)


def _parse_lines(value: str) -> list[str]:
    """Parse a list of text lines as Tox 4 wants to output the tags."""
    return [line for line in value.splitlines() if line]


def remove_prefix(value: str, prefix: str) -> str:
    """Remove a string's prefix if it is there.

    Will be replaced with str.removeprefix() once we can depend on Python 3.9+.
    """
    parts: Final = value.partition(prefix)
    return parts[2] if parts[1] and not parts[0] else value


def parse_showconfig(
    filename: pathlib.Path = DEFAULT_FILENAME,
    *,
    env: dict[str, str] | None = None,
    tox_invoke: list[str | pathlib.Path] | None = None,
) -> dict[str, TestenvTags]:
    """Run `tox --showconfig` and look for tags in its output."""
    if tox_invoke is None:
        tox_invoke = [sys.executable, "-u", "-m", "tox"]
    tox_cmd: Final = [
        *tox_invoke,
        "--showconfig" if HAVE_MOD_TOX_3 else "config",
        "-c",
        filename,
        "-e",
        "ALL",
    ]
    contents: Final = subprocess.run(
        tox_cmd,
        check=True,
        encoding="UTF-8",
        env=env,
        shell=False,  # noqa: S603
        stdout=subprocess.PIPE,
    ).stdout
    assert isinstance(contents, str)

    cfgp: Final = configparser.ConfigParser(interpolation=None)
    cfgp.read_string(contents)

    return {
        name: TestenvTags(
            cfg_name=cfg_name,
            name=name,
            tags=_parse_strlist(tags) if HAVE_MOD_TOX_3 else _parse_lines(tags),
        )
        for cfg_name, name, tags in (
            (cfg_name, name, env["tags"])
            for cfg_name, name, env in (
                (cfg_name, remove_prefix(cfg_name, "testenv:"), env)
                for cfg_name, env in cfgp.items()
            )
            if cfg_name != name
        )
    }
