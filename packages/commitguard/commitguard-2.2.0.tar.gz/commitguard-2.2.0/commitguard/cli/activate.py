from argparse import Namespace

from commitguard.config import (
    get_pyproject_toml_path,
    load_config_from_pyproject_toml,
)
from commitguard.hooks import PreCommitHook
from commitguard.settings import CommitguardSettings, Mode
from commitguard.terminal import Terminal


def install_hooks(term: Terminal, args: Namespace) -> None:
    pre_commit_hook = PreCommitHook()
    pyproject_toml = get_pyproject_toml_path()
    config = load_config_from_pyproject_toml(pyproject_toml)

    if pre_commit_hook.exists() and not args.force:
        term.warning(
            "commitguard pre-commit hook is already"
            f" installed at {pre_commit_hook}."
        )
        with term.indent():
            term.print()
            term.info(
                "Run 'commitguard activate --force' to override the current "
                "installed pre-commit hook."
            )
            term.info(
                "Run 'commitguard check' to validate the current status of "
                "the installed pre-commit hook."
            )
    else:
        if args.mode:
            mode = Mode.from_string(args.mode)
        else:
            mode = config.get_mode().get_effective_mode()

        if not config.has_commitguard_config():
            settings = CommitguardSettings(mode=mode)
            config.settings = settings
            settings.write(pyproject_toml)

            term.ok(f"commitguard settings written to {pyproject_toml}.")
        elif args.force:
            settings = config.settings  # type: ignore
            settings.mode = mode
            settings.write(pyproject_toml)

            term.ok(f"commitguard settings written to {pyproject_toml}.")

        pre_commit_hook.write(mode=mode)

        term.ok(
            f"commitguard pre-commit hook installed at {pre_commit_hook}"
            f" using {mode} mode."
        )
