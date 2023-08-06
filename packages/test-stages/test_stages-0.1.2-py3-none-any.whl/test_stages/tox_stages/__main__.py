# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""The main tox-stages command-line executable."""

from __future__ import annotations

import dataclasses
import subprocess
import sys
from typing import TYPE_CHECKING

import tox_trivtags
from test_stages import cmd


if tox_trivtags.HAVE_MOD_TOX_3 or tox_trivtags.HAVE_MOD_TOX_4:
    from tox_trivtags import parse as ttt_parse

if TYPE_CHECKING:
    import pathlib
    from typing import Final


@dataclasses.dataclass(frozen=True)
class Config(cmd.Config):
    """Also store the path to the Tox executable if found."""

    tox_program: list[str | pathlib.Path] | None = None


@cmd.click_available()
def _cmd_available(cfg: cmd.Config) -> bool:
    """Check whether we can parse the Tox configuration in any of the supported ways.

    Currently the only supported way is `tox --showconfig`.
    """
    assert isinstance(cfg, Config)  # noqa: S101  # mypy needs this
    return cfg.tox_program is not None


@cmd.click_run()
def _cmd_run(cfg: cmd.Config, stages: list[cmd.TestStage], extra_args: list[str]) -> None:
    """Run the Tox environments in groups."""
    toxdir = cfg.filename.parent

    def run_group(group: list[cmd.TestEnv], *, parallel: bool) -> None:
        """Run the stages in a single group."""
        if not isinstance(cfg, Config) or cfg.tox_program is None:
            #  _tox_get_envs() really should have taken care of that
            sys.exit(f"Internal error: tox-stages run_group: Config? {cfg!r}")

        names: Final = ",".join(env.name for env in group)
        print(f"\n=== Running Tox environments: {names}\n")  # noqa: T201
        run_parallel = (
            (["-p", "all"] if parallel else [])
            if tox_trivtags.HAVE_MOD_TOX_3
            else (["run-parallel"] if parallel else ["run"])
        )
        tox_cmd: Final = [*cfg.tox_program, *run_parallel, "-e", names, *extra_args]
        res: Final = subprocess.run(
            tox_cmd,
            check=False,
            cwd=toxdir,
            env=cfg.utf8_env,
            shell=False,  # noqa: S603
        )
        if res.returncode != 0:
            sys.exit(f"Tox failed for the {names} environments")

    for desc in stages:
        run_group(desc.envlist, parallel=desc.parallel)

    print("\n=== All Tox environment groups passed!")  # noqa: T201


def _tox_get_envs(cfg: cmd.Config) -> list[cmd.TestEnv]:
    """Get all the Tox environments from the config file."""
    assert isinstance(cfg, Config)  # noqa: S101  # mypy needs this
    if cfg.tox_program is None:
        sys.exit("No tox program found or specified")
    tcfg: Final = ttt_parse.parse_showconfig(
        filename=cfg.filename, env=cfg.utf8_env, tox_invoke=cfg.tox_program
    )
    return [cmd.TestEnv(name, env.tags) for name, env in tcfg.items()]


def _find_tox_program() -> list[str | pathlib.Path] | None:
    """Figure out how to invoke Tox.

    For the present, only a Tox installation in the current Python interpreter's
    package directories is supported, since we need to be sure that we can rely on
    the `tox-trivtags` package being installed.

    Also, we only support Tox 3.x for the present.
    """
    if not tox_trivtags.HAVE_MOD_TOX_3 and not tox_trivtags.HAVE_MOD_TOX_4:
        return None

    return [sys.executable, "-m", "tox"]


@cmd.click_main(
    prog="tox-stages",
    prog_help="Run Tox environments in groups, stop on failure.",
    filename="tox.ini",
    filename_help="the path to the Tox config file to parse",
    get_all_envs=_tox_get_envs,
)
def main(cfg: cmd.Config) -> cmd.Config:
    """Return our `Config` object with the path to Tox if found."""
    return Config(**dataclasses.asdict(cfg), tox_program=_find_tox_program())


main.add_command(_cmd_available)
main.add_command(_cmd_run)


if __name__ == "__main__":
    # pylint: disable-next=no-value-for-parameter
    main()
