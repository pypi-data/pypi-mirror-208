<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# tox-stages - run Tox environments in groups, stop on failure

## Synopsis

``` sh
tox-stages [-f filename] available
tox-stages [-f filename] run [-A arg...] [-p spec] stage...
```

## Description

The `tox-stages` tool is used to run Tox test environments in several
stages, one or more environments running in parallel at each stage.
If any of the test environments run at some stage shoud fail,
`tox-stages` will stop, not run anything further, and exit with
a non-zero exit code.
This allows quick static check tools like e.g. `ruff` to stop
the testing process early, and also allows scenarios like running
all the static check tools before the package's unit or functional
tests to avoid unnecessary failures on simple errors.

## Tagging Tox test environments

The `tox-stages` tool expects to be able to invoke an installation of
Tox that will load the `tox_trivtags` plugin module distributed as part of
the `test-stages` library.
This module will add a "tags" list of strings to the definition of each
Tox environment; those tags can be specified in the `tox.ini` file as follows:

``` ini
[testenv:format]
skip_install = True
tags =
  check
  format
deps =
  ...
```

## Subcommands

### available - can the tox-stages tool be run on this system

The `tox-stages available` subcommand exits with a code of zero
(indicating success) if there is a suitable version of Tox installed in
the same Python execution environment as the `tox-stages` tool itself.

### run - run some Tox environments in stages

The `tox-stages run` subcommand starts the process of running Tox test
environments, grouped in stages.
If any of the test environments run at some stage shoud fail,
`tox-stages` will stop, not run anything further, and exit with
a non-zero exit code.

The `run` subcommand accepts the following options:

- `--arg argument` / `-A argument` <br/>
  Pass an additional command-line argument to each Tox invocation.
  This option may be specified more than once, and the arguments will be
  passed in the order given.
- `--parallel spec` / `-p spec` <br/>
  Specify which stages to run in parallel.
  The `spec` parameter is a list of stage indices (1, 2, etc.) or
  ranges (4-6); the tests in the specified stages will be run in
  parallel, while the tests in the rest of the stages will not.
  By default, all tests are run in parallel.
  The special values "" (an empty string), "0" (a single character,
  the digit zero), or "none" will be treated as an empty set, and
  no tests will be run in parallel.
- `stage...` <br/>
  The positional arguments to the `run` subcommand are interpreted as
  test stage specifications as described in
  [the parse-stages library's documentation][ringlet-parse-stages].
  If no stage specifications are given on the command line,
  `tox-stages` will read the `pyproject.toml` file in the same
  directory as the `tox.ini` file, and will look for a
  `tool.test-stages.stages` list of strings to use.

## Files

If no stage specifications are given to the `run` subcommand,
the `pyproject.toml` file is read and its `tool.test-stages.stages`
variable (expected to be a list of strings) is used instead.

## Examples

Run all the stages as defined in the `pyproject.toml` file's
`tool.test-stages.stages` parameter:

``` sh
tox-stages run
```

Run a specific set of stages, passing `-- -k slug` as additional
Tox arguments so that e.g. a `pytest` environment that uses the Tox
`{posargs}` variable may only run a selected subset of tests:

``` sh
tox-stages -A -- -A -k -A slug @check unit-tests
```

Execute a somewhat more complicated recipe:

- first, run all test environments with names containing "ruff" in parallel
- then, run the rest of the test environments marked with the "check" tag,
  but not marked with the "manual" tag, one by one
- then, run all test environments with names containing "unit" in parallel
- finally, run the rest of the test environments marked with the "tests" tag,
  but not marked with the "manual" tag, in parallel

``` sh
tox-stages -p 1,3-4 ruff '@check and not @manual' unit '@tests and not @manual'
```

## Author

The `tox-stages` tool, along with its documentation, is developed as part of
the `test-stages` library by [Peter Pentchev][roam] in
[a GitLab repository][gitlab].
This documentation is hosted at [Ringlet][ringlet-test-stages] with
a copy at [ReadTheDocs][readthedocs].

[gitlab]: https://gitlab.com/ppentchev/test-stages "The test-stages GitLab repository"
[roam]: mailto:roam@ringlet.net "Peter Pentchev"
[readthedocs]: https://test-stages.readthedocs.io/en/latest/
[ringlet-parse-stages]: https://devel.ringlet.net/devel/parse-stages "Parse a mini-language for selecting objects by tag or name"
[ringlet-test-stages]: https://devel.ringlet.net/devel/test-stages/ "The Ringlet test-stages homepage"
