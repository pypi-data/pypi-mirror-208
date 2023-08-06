# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Parse a list of tags in the Tox configuration.

Inspired by https://github.com/tox-dev/tox-tags
"""

from __future__ import annotations

import logging
import typing

import distlib.database as dist_database
import distlib.version as dist_version


if typing.TYPE_CHECKING:
    from typing import Final


def _get_tox_distribution() -> dist_database.InstalledDistribution | None:
    """Figure out whether Tox is installed."""

    def no_messages(_evt: logging.LogRecord) -> bool:
        """Do not output any logging messages, none at all."""
        return False

    logging.getLogger("distlib.database").addFilter(no_messages)
    logging.getLogger("distlib.metadata").addFilter(no_messages)
    dist: Final = dist_database.DistributionPath(include_egg=True).get_distribution("tox")
    logging.getLogger("distlib.database").removeFilter(no_messages)
    logging.getLogger("distlib.metadata").removeFilter(no_messages)
    return dist


_TOX_DIST: Final = _get_tox_distribution()

if _TOX_DIST is None:
    HAVE_MOD_TOX_3 = False
    HAVE_MOD_TOX_4 = False
else:
    _TOX_VERSION: Final = dist_version.NormalizedVersion(_TOX_DIST.version)

    HAVE_MOD_TOX_3 = (
        dist_version.NormalizedVersion("3") <= _TOX_VERSION < dist_version.NormalizedVersion("4")
    )

    HAVE_MOD_TOX_4 = (
        dist_version.NormalizedVersion("4") <= _TOX_VERSION < dist_version.NormalizedVersion("5")
    )


if HAVE_MOD_TOX_3:
    import tox
    import tox.config

    @tox.hookimpl
    def tox_addoption(parser: tox.config.Parser) -> None:
        """Parse a testenv's "tags" attribute as a list of lines."""
        parser.add_testenv_attribute(
            "tags", "line-list", "A list of tags describing this test environment", default=[]
        )


if HAVE_MOD_TOX_4:
    from typing import List

    import tox.plugin as t_plugin

    if typing.TYPE_CHECKING:
        import tox.config.sets as t_sets
        import tox.session.state as t_state

    @t_plugin.impl
    def tox_add_env_config(
        env_conf: t_sets.EnvConfigSet,
        state: t_state.State,  # noqa: ARG001
    ) -> None:
        """Parse a testenv's "tags" attribute as a list of lines."""
        env_conf.add_config(
            keys=["tags"],
            of_type=List[str],
            default=[],
            desc="A list of tags describing this test environment",
        )
