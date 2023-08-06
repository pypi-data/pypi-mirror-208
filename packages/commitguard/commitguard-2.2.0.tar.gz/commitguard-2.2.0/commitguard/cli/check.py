from argparse import Namespace
from pathlib import Path

from commitguard.config import (
    COMMITGUARD_SECTION,
    get_pyproject_toml_path,
    load_config_from_pyproject_toml,
)
from commitguard.hooks import PreCommitHook
from commitguard.precommit.run import (
    CheckPluginError,
    CheckPluginWarning,
    check_plugin,
    commitguard_module_path,
)
from commitguard.settings import Mode
from commitguard.terminal import Terminal


# pylint: disable=unused-argument
def check_hooks(term: Terminal, args: Namespace) -> None:
    pre_commit_hook = PreCommitHook()
    check_pre_commit_hook(term, pre_commit_hook)

    pyproject_toml = get_pyproject_toml_path()

    check_config(term, pyproject_toml, pre_commit_hook)


def check_pre_commit_hook(
    term: Terminal, pre_commit_hook: PreCommitHook
) -> None:
    if pre_commit_hook.exists():
        if pre_commit_hook.is_commitguard_pre_commit_hook():
            term.ok("commitguard pre-commit hook is active.")

            if pre_commit_hook.is_current_commitguard_pre_commit_hook():
                term.ok("commitguard pre-commit hook is up-to-date.")
            else:
                term.warning(
                    "commitguard pre-commit hook is outdated. Please run "
                    "'commitguard activate --force' to update your pre-commit "
                    "hook."
                )

            hook_mode = pre_commit_hook.read_mode()
            if hook_mode == Mode.UNKNOWN:
                term.warning(
                    f"Unknown commitguard mode in {str(pre_commit_hook)}. "
                    f'Falling back to "{str(hook_mode.get_effective_mode())}" '
                    "mode."
                )
        else:
            term.error(
                "commitguard pre-commit hook is not active. But a different "
                f"pre-commit hook has been found at {str(pre_commit_hook)}."
            )

    else:
        term.error(
            "commitguard pre-commit hook not active. Please run 'commitguard "
            "activate'."
        )


def check_config(
    term: Terminal,
    pyproject_toml: Path,
    pre_commit_hook: PreCommitHook,
) -> None:
    if not pyproject_toml.exists():
        term.error(
            f"Missing {str(pyproject_toml)} file. Please add a pyproject.toml "
            f'file and include a "{COMMITGUARD_SECTION}" section.'
        )
    else:
        config = load_config_from_pyproject_toml(pyproject_toml)
        if not config.has_commitguard_config():
            term.error(
                f"commitguard is not enabled in your {str(pyproject_toml)} file."
                f' Please add a "{COMMITGUARD_SECTION}" section.'
            )
        elif pre_commit_hook.exists():
            config_mode = config.get_mode()
            hook_mode = pre_commit_hook.read_mode()

            if config_mode == Mode.UNDEFINED:
                term.warning(
                    f"commitguard mode is not defined in {str(pyproject_toml)}."
                )
            elif config_mode == Mode.UNKNOWN:
                term.warning(
                    f"Unknown commitguard mode in {str(pyproject_toml)}."
                )

            elif (
                config_mode.get_effective_mode()
                != hook_mode.get_effective_mode()
            ):
                term.warning(
                    f'commitguard mode "{str(hook_mode)}" in pre-commit '
                    f"hook {str(pre_commit_hook)} differs from "
                    f'mode "{str(config_mode)}" in {str(pyproject_toml)}.'
                )

            term.info(
                f'Using commitguard mode "{str(hook_mode.get_effective_mode())}".'
            )

            plugins = config.get_pre_commit_script_names()
            if not plugins:
                term.error(
                    "No commitguard plugin is activated in "
                    f"{str(pyproject_toml)} for your pre commit hook. Please "
                    'add a "pre-commit = [plugin1, plugin2]" setting.'
                )
            else:
                with commitguard_module_path():
                    for name in plugins:
                        result = check_plugin(name)
                        if result:
                            if isinstance(result, CheckPluginError):
                                term.error(str(result))
                            elif isinstance(result, CheckPluginWarning):
                                term.warning(str(result))
                            else:
                                term.info(str(result))
                        else:
                            term.ok(f'Plugin "{name}" active and loadable.')
