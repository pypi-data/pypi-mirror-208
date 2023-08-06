import sys
import unittest
from argparse import Namespace
from unittest.mock import MagicMock, call

from commitguard.cli.check import (
    check_config,
    check_hooks,
    check_pre_commit_hook,
)
from commitguard.config import COMMITGUARD_SECTION
from commitguard.hooks import PreCommitHook, get_pre_commit_hook_path
from commitguard.settings import Mode
from commitguard.template import POETRY_SHEBANG, TEMPLATE_VERSION
from commitguard.utils import get_pyproject_toml_path
from tests import tempgitdir


class CheckCliTestCase(unittest.TestCase):
    def test_no_pre_commit_hooks_no_pyproject_toml(self):
        term = MagicMock()
        args = Namespace()

        with tempgitdir() as tmpdir:
            check_hooks(term, args)

        term.ok.assert_not_called()
        term.warning.assert_not_called()
        term.info.assert_not_called()
        self.assertEqual(term.error.call_count, 2)
        term.error.assert_has_calls(
            (
                call(
                    "commitguard pre-commit hook not active. Please run "
                    "'commitguard activate'."
                ),
                call(
                    f"Missing {tmpdir}/pyproject.toml file. Please add a "
                    'pyproject.toml file and include a "tool.commitguard" '
                    "section."
                ),
            )
        )

    def test_no_pre_commit_hooks_no_commitguard_settings(self):
        term = MagicMock()
        args = Namespace()

        with tempgitdir() as tmpdir:
            pyproject_toml = tmpdir / "pyproject.toml"
            pyproject_toml.touch()

            check_hooks(term, args)

        term.ok.assert_not_called()
        term.warning.assert_not_called()
        term.info.assert_not_called()
        self.assertEqual(term.error.call_count, 2)
        term.error.assert_has_calls(
            (
                call(
                    "commitguard pre-commit hook not active. Please run "
                    "'commitguard activate'."
                ),
                call(
                    f"commitguard is not enabled in your {tmpdir}/pyproject.toml "
                    'file. Please add a "tool.commitguard" section.'
                ),
            )
        )

    def test_all_checks_success(self):
        term = MagicMock()
        args = Namespace()

        with tempgitdir() as tmpdir:
            pyproject_toml = tmpdir / "pyproject.toml"
            pyproject_toml.write_text(
                """[tool.commitguard]
mode = "poetry"
pre-commit = ["plugin1"]
""",
                encoding="utf8",
            )
            pre_commit_hook = PreCommitHook()
            pre_commit_hook.write(mode=Mode.POETRY)
            dot_commitguard_dir = tmpdir / ".commitguard"
            dot_commitguard_dir.mkdir()
            plugin1 = dot_commitguard_dir / "plugin1.py"
            plugin1.write_text(
                """
def precommit(*args):
    pass
            """,
                encoding="utf8",
            )

            check_hooks(term, args)

        self.assertEqual(term.ok.call_count, 3)
        term.ok.assert_has_calls(
            (
                call("commitguard pre-commit hook is active."),
                call("commitguard pre-commit hook is up-to-date."),
                call('Plugin "plugin1" active and loadable.'),
            )
        )
        term.warning.assert_not_called()
        term.info.assert_called_once_with('Using commitguard mode "poetry".')
        term.error.assert_not_called()

        del sys.modules["plugin1"]


class CheckPreCommitHookTestCase(unittest.TestCase):
    def test_no_precommit_hook(self):
        term = MagicMock()

        with tempgitdir():
            pre_commit_hook = PreCommitHook()

            check_pre_commit_hook(term, pre_commit_hook)

        term.ok.assert_not_called()
        term.warning.assert_not_called()
        term.info.assert_not_called()
        term.error.assert_called_once_with(
            "commitguard pre-commit hook not active. Please run "
            "'commitguard activate'."
        )

    def test_no_commitguard_precommit_hook(self):
        term = MagicMock()

        with tempgitdir():
            pre_commit_hook_path = get_pre_commit_hook_path()
            pre_commit_hook_path.write_text(
                '#!/bin/sh\necho "Hello World\n"', encoding="utf8"
            )
            pre_commit_hook = PreCommitHook()

            check_pre_commit_hook(term, pre_commit_hook)

        term.ok.assert_not_called()
        term.warning.assert_not_called()
        term.info.assert_not_called()
        term.error.assert_called_once_with(
            "commitguard pre-commit hook is not active. But a different "
            f"pre-commit hook has been found at {pre_commit_hook_path}."
        )

    def test_outdated_precommit_hook(self):
        term = MagicMock()

        with tempgitdir():
            pre_commit_hook_path = get_pre_commit_hook_path()
            pre_commit_hook_path.write_text(
                f"""!#{POETRY_SHEBANG}

import sys

try:
    from commitguard.precommit import run
    sys.exit(run())
except ImportError:
    pass
            """,
                encoding="utf8",
            )
            pre_commit_hook = PreCommitHook()

            check_pre_commit_hook(term, pre_commit_hook)

        term.ok.assert_called_once_with(
            "commitguard pre-commit hook is active."
        )
        term.warning.assert_called_once_with(
            "commitguard pre-commit hook is outdated. Please run "
            "'commitguard activate --force' to update your pre-commit "
            "hook."
        )
        term.info.assert_not_called()
        term.error.assert_not_called()

    def test_unknown_mode(self):
        term = MagicMock()

        with tempgitdir():
            pre_commit_hook_path = get_pre_commit_hook_path()
            pre_commit_hook_path.write_text(
                f"""#!/bin/sh
# meta = {{ version = {TEMPLATE_VERSION} }}

import sys

try:
    from commitguard.precommit import run
    sys.exit(run())
except ImportError:
    pass
            """,
                encoding="utf8",
            )
            pre_commit_hook = PreCommitHook()

            check_pre_commit_hook(term, pre_commit_hook)

        self.assertEqual(term.ok.call_count, 2)
        term.ok.assert_has_calls(
            (
                call("commitguard pre-commit hook is active."),
                call("commitguard pre-commit hook is up-to-date."),
            )
        )
        term.warning.assert_called_once_with(
            f"Unknown commitguard mode in {pre_commit_hook}. "
            f'Falling back to "pythonpath" mode.'
        )
        term.info.assert_not_called()
        term.error.assert_not_called()

    def test_is_active(self):
        term = MagicMock()

        with tempgitdir():
            pre_commit_hook = PreCommitHook()
            pre_commit_hook.write(mode=Mode.POETRY)

            check_pre_commit_hook(term, pre_commit_hook)

        self.assertEqual(term.ok.call_count, 2)
        term.ok.assert_has_calls(
            (
                call("commitguard pre-commit hook is active."),
                call("commitguard pre-commit hook is up-to-date."),
            )
        )
        term.warning.assert_not_called()
        term.info.assert_not_called()
        term.error.assert_not_called()


class CheckConfigTestCase(unittest.TestCase):
    def test_no_pyproject_toml(self):
        term = MagicMock()

        with tempgitdir():
            pre_commit_hook = PreCommitHook()
            pyproject_toml = get_pyproject_toml_path()

            check_config(term, pyproject_toml, pre_commit_hook)

        term.ok.assert_not_called()
        term.warning.assert_not_called()
        term.info.assert_not_called()
        term.error.assert_called_once_with(
            f"Missing {pyproject_toml} file. Please add a "
            'pyproject.toml file and include a "tool.commitguard" '
            "section."
        )

    def test_no_commitguard_section(self):
        term = MagicMock()

        with tempgitdir():
            pre_commit_hook = PreCommitHook()
            pyproject_toml = get_pyproject_toml_path()
            pyproject_toml.touch()

            check_config(term, pyproject_toml, pre_commit_hook)

        term.ok.assert_not_called()
        term.warning.assert_not_called()
        term.info.assert_not_called()
        term.error.assert_called_once_with(
            f"commitguard is not enabled in your {pyproject_toml} file."
            f' Please add a "{COMMITGUARD_SECTION}" section.'
        )

    def test_undefined_mode(self):
        term = MagicMock()

        with tempgitdir():
            pre_commit_hook = PreCommitHook()
            pre_commit_hook.write(mode=Mode.POETRY)
            pyproject_toml = get_pyproject_toml_path()
            pyproject_toml.write_text(
                "[tool.commitguard]\npre-commit = []", encoding="utf8"
            )

            check_config(term, pyproject_toml, pre_commit_hook)

        term.ok.assert_not_called()
        term.warning.assert_called_once_with(
            f"commitguard mode is not defined in {pyproject_toml}."
        )
        term.info.assert_called_once_with('Using commitguard mode "poetry".')
        term.error.assert_called_once_with(
            "No commitguard plugin is activated in "
            f"{pyproject_toml} for your pre commit hook. Please "
            'add a "pre-commit = [plugin1, plugin2]" setting.'
        )

    def test_unknown_mode(self):
        term = MagicMock()

        with tempgitdir():
            pre_commit_hook = PreCommitHook()
            pre_commit_hook.write(mode=Mode.POETRY)
            pyproject_toml = get_pyproject_toml_path()
            pyproject_toml.write_text(
                "[tool.commitguard]\nmode = 'foo'\npre-commit = []",
                encoding="utf8",
            )

            check_config(term, pyproject_toml, pre_commit_hook)

        term.ok.assert_not_called()
        term.warning.assert_called_once_with(
            f"Unknown commitguard mode in {pyproject_toml}."
        )
        term.info.assert_called_once_with('Using commitguard mode "poetry".')
        term.error.assert_called_once_with(
            "No commitguard plugin is activated in "
            f"{pyproject_toml} for your pre commit hook. Please "
            'add a "pre-commit = [plugin1, plugin2]" setting.'
        )

    def test_different_mode(self):
        term = MagicMock()

        with tempgitdir():
            pre_commit_hook = PreCommitHook()
            pre_commit_hook.write(mode=Mode.POETRY)
            pyproject_toml = get_pyproject_toml_path()
            pyproject_toml.write_text(
                "[tool.commitguard]\nmode = 'pythonpath'\npre-commit = []",
                encoding="utf8",
            )

            check_config(term, pyproject_toml, pre_commit_hook)

        term.ok.assert_not_called()
        term.warning.assert_called_once_with(
            f'commitguard mode "poetry" in pre-commit '
            f"hook {pre_commit_hook} differs from "
            f'mode "pythonpath" in {pyproject_toml}.'
        )
        term.info.assert_called_once_with('Using commitguard mode "poetry".')
        term.error.assert_called_once_with(
            "No commitguard plugin is activated in "
            f"{pyproject_toml} for your pre commit hook. Please "
            'add a "pre-commit = [plugin1, plugin2]" setting.'
        )

    def test_no_plugin(self):
        term = MagicMock()

        with tempgitdir():
            pre_commit_hook = PreCommitHook()
            pre_commit_hook.write(mode=Mode.POETRY)
            pyproject_toml = get_pyproject_toml_path()
            pyproject_toml.write_text(
                "[tool.commitguard]\nmode = 'poetry'\npre-commit = []",
                encoding="utf8",
            )

            check_config(term, pyproject_toml, pre_commit_hook)

        term.ok.assert_not_called()
        term.warning.assert_not_called()
        term.info.assert_called_once_with('Using commitguard mode "poetry".')
        term.error.assert_called_once_with(
            "No commitguard plugin is activated in "
            f"{pyproject_toml} for your pre commit hook. Please "
            'add a "pre-commit = [plugin1, plugin2]" setting.'
        )

    def test_plugin_not_loadable(self):
        term = MagicMock()

        with tempgitdir():
            pre_commit_hook = PreCommitHook()
            pre_commit_hook.write(mode=Mode.POETRY)
            pyproject_toml = get_pyproject_toml_path()
            pyproject_toml.write_text(
                "[tool.commitguard]\nmode = 'poetry'\npre-commit = ['plugin1']",
                encoding="utf8",
            )

            check_config(term, pyproject_toml, pre_commit_hook)

        term.ok.assert_not_called()
        term.warning.assert_not_called()
        term.info.assert_called_once_with('Using commitguard mode "poetry".')
        term.error.assert_called_once_with(
            '"plugin1" is not a valid commitguard plugin. '
            "No module named 'plugin1'"
        )

    def test_plugin_no_precommit_function(self):
        term = MagicMock()

        with tempgitdir() as tmpdir:
            pre_commit_hook = PreCommitHook()
            pre_commit_hook.write(mode=Mode.POETRY)
            pyproject_toml = get_pyproject_toml_path()
            pyproject_toml.write_text(
                "[tool.commitguard]\nmode = 'poetry'\npre-commit = ['plugin1']",
                encoding="utf8",
            )
            dot_commitguard_dir = tmpdir / ".commitguard"
            dot_commitguard_dir.mkdir()
            plugin1 = dot_commitguard_dir / "plugin1.py"
            plugin1.touch()

            check_config(term, pyproject_toml, pre_commit_hook)

        term.ok.assert_not_called()
        term.warning.assert_not_called()
        term.info.assert_called_once_with('Using commitguard mode "poetry".')
        term.error.assert_called_once_with(
            'Plugin "plugin1" has no precommit '
            "function. The function is required to run"
            " the plugin as git pre commit hook."
        )

        del sys.modules["plugin1"]

    def test_plugin_old_precommit_signature(self):
        term = MagicMock()

        with tempgitdir() as tmpdir:
            pre_commit_hook = PreCommitHook()
            pre_commit_hook.write(mode=Mode.POETRY)
            pyproject_toml = get_pyproject_toml_path()
            pyproject_toml.write_text(
                "[tool.commitguard]\nmode = 'poetry'\npre-commit = ['plugin1']",
                encoding="utf8",
            )
            dot_commitguard_dir = tmpdir / ".commitguard"
            dot_commitguard_dir.mkdir()
            plugin1 = dot_commitguard_dir / "plugin1.py"
            plugin1.write_text(
                """
def precommit():
    pass
            """,
                encoding="utf8",
            )

            check_config(term, pyproject_toml, pre_commit_hook)

        term.ok.assert_not_called()
        term.warning.assert_called_once_with(
            'Plugin "plugin1" uses a deprecated '
            "signature for its precommit function. It "
            "is missing the **kwargs parameter."
        )
        term.info.assert_called_once_with('Using commitguard mode "poetry".')
        term.error.assert_not_called()

        del sys.modules["plugin1"]

    def test_success(self):
        term = MagicMock()

        with tempgitdir() as tmpdir:
            pre_commit_hook = PreCommitHook()
            pre_commit_hook.write(mode=Mode.POETRY)
            pyproject_toml = get_pyproject_toml_path()
            pyproject_toml.write_text(
                "[tool.commitguard]\nmode = 'poetry'\npre-commit = ['plugin1']",
                encoding="utf8",
            )
            dot_commitguard_dir = tmpdir / ".commitguard"
            dot_commitguard_dir.mkdir()
            plugin1 = dot_commitguard_dir / "plugin1.py"
            plugin1.write_text(
                """
def precommit(*args):
    pass
            """,
                encoding="utf8",
            )

            check_config(term, pyproject_toml, pre_commit_hook)

        term.ok.assert_called_once_with('Plugin "plugin1" active and loadable.')
        term.warning.assert_not_called()
        term.info.assert_called_once_with('Using commitguard mode "poetry".')
        term.error.assert_not_called()

        del sys.modules["plugin1"]
