<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# Changelog

All notable changes to the test-stages project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2023-03-13

### Incompatible changes

- tox-trivtags:
    - drop the `tox_trivtags.parse.parse_config()` function, running
      `tox --showconfig` is the only supported method now

### Fixes

- tox-stages:
    - minor refactoring and fixes suggested by Ruff
- tox-trivtags:
    - use the correct way to ignore a specific Ruff check for the whole
      file instead of telling Ruff to skip that file entirely!
    - minor fixes suggested by Ruff
- testing framework:
    - correct the `tox.envlist` list in the `tox.ini` file

### Additions

- add the beginnings of [MkDocs-based][tool-mkdocs] documentation, hosted
  [at the Ringlet test-stages webpage][ringlet-test-stages]
  for the latest release and [at ReadTheDocs][readthedocs] for
  the latest version from the Git repository
- add manual page for the `tox-stages` tool in the mdoc format
- add a `.gitignore` file, mainly so that the `reuse` tool can be run even
  in the presence of some test-related files and directories
- add a `selftest` module (not installed in the wheel) that runs
  the `tox-stages` tool itself on a copy of the source tree
- build system:
    - add the "Typing :: Typed" PyPI trove classifier
    - specify the project's two-clause BSD license
- tox-stages:
    - add support for Tox 4.x
    - allow the `tox-stages` command-line tool to be invoked via `python3 -m`
    - add the `--arg` / `-A` option to pass additional arguments to Tox
    - add the `--parallel` / `-p` option to specify which stages should run
      their tests in parallel
- testing framework:
    - add the `reuse` Tox test environment for checking the SPDX tags manually

### Other changes

- use SPDX license tags
- move the changelog file into the MkDocs-managed `docs/` directory
- point to the Ringlet homepage in the package metadata and the README file
- tox-stages:
    - reformat the import statements using Ruff's isort implementation
    - use `tox run-parallel` when running with Tox 4.x
- tox-trivtags:
    - reformat the import statements using Ruff's isort implementation
    - use `tox config` when running with Tox 4.x
- build system:
    - switch to hatch/hatchling for the PEP517 build
    - move the `contextlib-chdir` module from the installation requirements to
      the test ones, since we do not use it in the installed library
    - bump the `parse-stages` dependency version to 0.1.4 so that an empty
      set may be specified as an argument to the `--parallel` option
- testing framework:
    - Ruff:
        - move the Ruff configuration files from `.config/` to `config/`
        - run `ruff check ...` explicitly
        - enable all of the Ruff checks in the default (`ruff`) test environment
        - use ruff 0.0.265 and ignore some subprocess checks: we do check
        - remove them `EM` checks override, we do not raise any exceptions
    - Formatting:
        - rename the `black` and `black-reformat` Tox environments to
          `format` and `reformat` respectively and invoke Ruff's isort
          implementation in both
        - specify Python 3.8 as the target version
    - Pylint:
        - remove the `empty-comment` plugin override, the SPDX license tags
          no longer cause it to complain
        - specify Python 3.8 as the target version
        - use pylint 2.17.x with no changes
    - update the `tox.ini` file for Tox 4.x (mostly a multiline list) and
      make the unit tests that run Tox 3.x revert those adaptations
    - use the `@manual` tag for Tox test environments that should only be
      run manually with care
    - drop the Tox environment that runs `flake8` and `pycodestyle`,
      we depend on Ruff for that

## [0.1.1] - 2023-02-07

### Fixes

- Include the changelog file and the `.config/ruff-*/pyproject.toml` files in
  the PyPI source distribution tarball.

## [0.1.0] - 2023-02-07

### Started

- First public release.

[readthedocs]: https://test-stages.readthedocs.io/en/latest/
[ringlet-test-stages]: https://devel.ringlet.net/devel/test-stages/ "The Ringlet test-stages homepage"
[tool-mkdocs]: https://www.mkdocs.org/ "Project documentation with Markdown"

[Unreleased]: https://gitlab.com/ppentchev/test-stages/-/compare/release%2F0.1.2...main
[0.1.2]: https://gitlab.com/ppentchev/test-stages/-/compare/release%2F0.1.1...release%2F0.1.2
[0.1.1]: https://gitlab.com/ppentchev/test-stages/-/compare/release%2F0.1.0...release%2F0.1.1
[0.1.0]: https://gitlab.com/ppentchev/test-stages/-/tags/release%2F0.1.0
