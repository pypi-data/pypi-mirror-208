<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# Run Tox tests in groups, stopping on errors

\[[Home][ringlet-test-stages] | [GitLab][gitlab] | [PyPI][pypi] | [ReadTheDocs][readthedocs]\]

The `test-stages` library provides command-line tools that wrap
Python test environment runners such as [Tox][tox] or [Nox][nox],
invoking them so as the various tests are run in parallel, in groups,
as specified on the command line.
This allows the fastest tests to be run first, and the slower ones to
only be started if it makes sense (e.g. if tools like [ruff] or [flake8]
did not uncover any trivial syntax errors).

The `tox-stages` tool runs Tox with the specified groups of test
environments, stopping if any of the tests in a group should fail.
This allows quick static check tools like e.g. `ruff` to stop
the testing process early, and also allows scenarios like running
all the static check tools before the package's unit or functional
tests to avoid unnecessary failures on simple errors.

The syntax for grouping the test environments to be run is described in
the [parse-stages] library's documentation.

[flake8]: https://github.com/pycqa/flake8 "The flake8 Python syntax and style checker"
[nox]: https://nox.thea.codes/ "The Nox test runner"
[parse-stages]: https://devel.ringlet.net/devel/parse-stages "Parse a mini-language for selecting objects by tag or name"
[ruff]: https://github.com/charliermarsh/ruff "Ruff, the extremely fast Python linter"
[tox]: https://tox.wiki/ "The Tox automation project"

## Running Tox tests in groups

The `tox-stages` tool may be invoked with a list of stages specified on
the command line:

``` sh
    tox-stages run @check @tests
```

If the `tox-stages run` command is invoked without any stage specifications,
the tool looks for the `stages` list of strings in the `[tool.test-stages]`
section of the `pyproject.toml` file:

``` toml
    [tool.test-stages]
    stages = ["ruff and not @manual", "@check", "@tests"]
```

## Author

The `test-stages` library is developed by [Peter Pentchev][roam] in
[a GitLab repository][gitlab].
This documentation is hosted at [Ringlet][ringlet-test-stages] with
a copy at [ReadTheDocs][readthedocs].

[gitlab]: https://gitlab.com/ppentchev/test-stages "The test-stages GitLab repository"
[pypi]: https://pypi.org/project/test-stages/ "The test-stages Python Package Index page"
[roam]: mailto:roam@ringlet.net "Peter Pentchev"
[readthedocs]: https://test-stages.readthedocs.io/en/latest/
[ringlet-test-stages]: https://devel.ringlet.net/devel/test-stages/ "The Ringlet test-stages homepage"
