
<p align="center">
    <em>Library for managing and writing git hooks in Python using `pyproject.toml` for its settings ✨</em>
</p>

## Installation

You can add commitguard in a few easy steps. First of all, install the dependency:

```shell
$ pip install commitguard

---> 100%

Successfully installed commitguard-0.1.0
```

or Using poetry

```shell
poetry add --dev commitguard
poetry run commitguard activate --mode poetry
```

The output of `commitguard activate` should be similar to:

```shell
 ✓ commitguard pre-commit hook installed at /commitguard/.git/hooks/pre-commit using poetry mode.
```

CommitGuard offers an adaptable plugin architecture where each plugin offers unique features that might require the installation of supplementary dependencies.

To manage these dependencies, CommitGuard presently supports three modes:


* `pythonpath` for dependency management via [pip]
* `poetry` for dependency management via [poetry] (recommended)
* `pipenv` for dependency management via [pipenv]

These modes dictate how CommitGuard, the plugins, and their dependencies are loaded during git hook execution.

## License

This project is licensed under the terms of the MIT license.
