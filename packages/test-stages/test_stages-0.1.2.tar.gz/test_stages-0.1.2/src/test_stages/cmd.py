# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Command-line tool helpers for the various test-stages implementations."""

from __future__ import annotations

import dataclasses
import functools
import pathlib
import sys
from typing import TYPE_CHECKING, NamedTuple

import click
import parse_stages as parse
import utf8_locale


if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any, Final, TypeVar

    # pylint: disable-next=invalid-name
    _T = TypeVar("_T")

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


TestEnv = parse.TaggedFrozen


class Stage(NamedTuple):
    """A stage specification and its boolean expression."""

    spec: str
    expr: parse.BoolExpr
    parallel: bool


class TestStage(NamedTuple):
    """A final representation of a test stage: the environments to run and some attributes."""

    envlist: list[TestEnv]
    """The list of environments to run at this stage."""

    parallel: bool
    """Run the environments in parallel."""


class StagesList:
    """Parse the `--parallel` command-line option argument into a set."""

    # pylint: disable=too-few-public-methods

    stages: set[int]
    """The selected stages, 1-based."""

    def __init__(self, value: str) -> None:
        """Record the selected set of stages."""
        self.stages = set(parse.parse_stage_ids(value))


@dataclasses.dataclass(frozen=True)
class Config:
    """Runtime configuration for the test runner tool."""

    filename: pathlib.Path
    get_all_envs: Callable[[Config], list[TestEnv]]
    stages: list[Stage] = dataclasses.field(default_factory=list)
    utf8_env: dict[str, str] = dataclasses.field(
        default_factory=lambda: utf8_locale.UTF8Detect().detect().env
    )


@dataclasses.dataclass
class ConfigHolder:
    """Hold a Config object."""

    cfg: Config | None = None


def _split_by(current: list[_T], func: Callable[[_T], bool]) -> tuple[list[_T], list[_T]]:
    """Split an ordered list of items in two by the given predicate."""
    res: Final[tuple[list[_T], list[_T]]] = ([], [])
    for stage in current:
        if func(stage):
            res[1].append(stage)
        else:
            res[0].append(stage)
    return res


def select_stages(cfg: Config, all_stages: list[TestEnv]) -> list[TestStage]:
    """Group the stages as specified."""

    def process_stage(
        acc: tuple[list[TestStage], list[TestEnv]], stage: Stage
    ) -> tuple[list[TestStage], list[TestEnv]]:
        """Stash the environments matched by a stage specification."""
        res, current = acc
        if not current:
            sys.exit(f"No test environments left for {stage.spec}")
        left, matched = _split_by(current, stage.expr.evaluate)
        if not matched:
            sys.exit(f"No test environments matched by {stage.spec}")
        res.append(TestStage(envlist=matched, parallel=stage.parallel))
        return res, left

    res_init: Final[list[TestStage]] = []
    return functools.reduce(process_stage, cfg.stages, (res_init, list(all_stages)))[0]


def extract_cfg(ctx: click.Context) -> Config:
    """Extract the Config object from the ConfigHolder."""
    cfg_hold: Final = ctx.find_object(ConfigHolder)
    # mypy needs these assertions
    assert cfg_hold is not None  # noqa: S101
    cfg: Final = cfg_hold.cfg
    assert cfg is not None  # noqa: S101
    return cfg


def _find_and_load_pyproject(startdir: pathlib.Path) -> dict[str, Any]:
    """Look for a pyproject.toml file, load it if found."""

    def _find_and_load(path: pathlib.Path) -> dict[str, Any] | None:
        """Check for a pyproject.toml file in the specified directory."""
        proj_file: Final = path / "pyproject.toml"
        if not proj_file.is_file():
            return None

        return tomllib.loads(proj_file.read_text(encoding="UTF-8"))

    # Maybe we should look in the parent directories, too... later.
    for path in (startdir,):
        found = _find_and_load(path)
        if found is not None:
            return found

    # No pyproject.toml file found, nothing to parse
    return {}


def click_available() -> Callable[[Callable[[Config], bool]], click.Command]:
    """Wrap an available() function, checking whether the test runner can be invoked."""

    def inner(handler: Callable[[Config], bool]) -> click.Command:
        """Wrap the available check function."""

        @click.command(name="available")
        @click.pass_context
        def real_available(ctx: click.Context) -> None:
            """Check whether the test runner is available."""
            sys.exit(0 if handler(extract_cfg(ctx)) else 1)

        return real_available

    return inner


def click_run() -> Callable[[Callable[[Config, list[TestStage], list[str]], None]], click.Command]:
    """Wrap a run() function, preparing the configuration."""

    def inner(handler: Callable[[Config, list[TestStage], list[str]], None]) -> click.Command:
        """Wrap the run function."""

        @click.command(name="run")
        @click.option(
            "-A",
            "--arg",
            type=str,
            multiple=True,
            help=(
                "an additional argument to pass to the test runner; "
                "may be specified multiple times"
            ),
        )
        @click.option(
            "-p",
            "--parallel",
            type=StagesList,
            help="specify which stages to run in parallel (e.g. '1,4-6')",
        )
        @click.argument("stages_spec", nargs=-1, required=False, type=str)
        @click.pass_context
        def real_run(
            ctx: click.Context, arg: list[str], parallel: StagesList | None, stages_spec: list[str]
        ) -> None:
            """Run the test environments in stages."""
            cfg_base: Final = extract_cfg(ctx)
            if not stages_spec:
                pyproj: Final = _find_and_load_pyproject(cfg_base.filename.parent)
                stages_spec = pyproj.get("tool", {}).get("test-stages", {}).get("stages", [])
                if not stages_spec:
                    sys.exit("No stages specified either on the command line or in pyproject.toml")

            pstages: Final = set(range(len(stages_spec))) if parallel is None else parallel.stages
            cfg: Final = dataclasses.replace(
                cfg_base,
                stages=[
                    Stage(spec, parse.parse_spec(spec), idx in pstages)
                    for idx, spec in enumerate(stages_spec)
                ],
            )
            ctx.obj.cfg = cfg

            handler(cfg, select_stages(cfg, cfg.get_all_envs(cfg)), arg)

        return real_run

    return inner


def click_main(
    prog: str,
    prog_help: str,
    filename: str,
    filename_help: str,
    get_all_envs: Callable[[Config], list[TestEnv]],
) -> Callable[[Callable[[Config], Config]], click.Group]:
    """Wrap a main() function, parsing the top-level options."""

    def inner(main: Callable[[Config], Config]) -> click.Group:
        """Wrap the main function."""

        @click.group(name=prog, help=prog_help)
        @click.option(
            "-f",
            "--filename",
            type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=pathlib.Path),
            default=filename,
            help=filename_help,
        )
        @click.pass_context
        def real_main(ctx: click.Context, filename: pathlib.Path) -> None:
            """Run Tox environments in groups, stop on failure."""
            ctx.ensure_object(ConfigHolder)
            ctx.obj.cfg = main(Config(filename=filename, get_all_envs=get_all_envs))

        return real_main

    return inner
