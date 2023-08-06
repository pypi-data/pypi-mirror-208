import unittest
from argparse import Namespace
from unittest.mock import MagicMock, call

from commitguard.cli.activate import install_hooks
from tests import tempgitdir

CONFIG = """
[tool.commitguard]
mode = "poetry"
"""


class ActivateCliTestCase(unittest.TestCase):
    def test_install_hooks(self):
        with tempgitdir() as tmpdir:
            pyproject_toml = tmpdir / "pyproject.toml"
            pyproject_toml.write_text(CONFIG, encoding="utf8")

            term = MagicMock()
            args = Namespace(force=False, mode=None)

            install_hooks(term, args)

            term.warning.assert_not_called()
            term.ok.assert_called_once_with(
                f"commitguard pre-commit hook installed at {tmpdir}/"
                ".git/hooks/pre-commit using poetry mode."
            )

    def test_install_exists(self):
        with tempgitdir() as tmpdir:
            pyproject_toml = tmpdir / "pyproject.toml"
            pyproject_toml.write_text(CONFIG, encoding="utf8")
            pre_commit = tmpdir / ".git" / "hooks" / "pre-commit"
            pre_commit.touch()

            term = MagicMock()
            args = Namespace(force=False, mode=None)

            install_hooks(term, args)

            term.ok.assert_not_called()
            term.warning.assert_called_once_with(
                f"commitguard pre-commit hook is already installed at {tmpdir}/"
                ".git/hooks/pre-commit."
            )
            term.info.assert_has_calls(
                (
                    call(
                        "Run 'commitguard activate --force' to override the "
                        "current installed pre-commit hook."
                    ),
                    call(
                        "Run 'commitguard check' to validate the current status "
                        "of the installed pre-commit hook."
                    ),
                )
            )

    def test_install_hooks_force(self):
        with tempgitdir() as tmpdir:
            pyproject_toml = tmpdir / "pyproject.toml"
            pyproject_toml.write_text(CONFIG, encoding="utf8")
            pre_commit = tmpdir / ".git" / "hooks" / "pre-commit"
            pre_commit.touch()

            term = MagicMock()
            args = Namespace(force=True, mode=None)

            install_hooks(term, args)

            term.warning.assert_not_called()
            term.ok.assert_has_calls(
                (
                    call(f"commitguard settings written to {pyproject_toml}."),
                    call(
                        f"commitguard pre-commit hook installed at {pre_commit}"
                        " using poetry mode."
                    ),
                )
            )

    def test_install_no_config(self):
        with tempgitdir() as tmpdir:
            term = MagicMock()
            args = Namespace(force=False, mode=None)

            install_hooks(term, args)

            term.warning.assert_not_called()
            term.ok.assert_has_calls(
                (
                    call(
                        "commitguard settings written to "
                        f"{tmpdir}/pyproject.toml."
                    ),
                    call(
                        f"commitguard pre-commit hook installed at {tmpdir}/"
                        ".git/hooks/pre-commit using pythonpath mode."
                    ),
                )
            )

    def test_install_hooks_with_mode(self):
        with tempgitdir() as tmpdir:
            pyproject_toml = tmpdir / "pyproject.toml"
            pyproject_toml.write_text(CONFIG, encoding="utf8")

            term = MagicMock()
            args = Namespace(force=False, mode="pythonpath")

            install_hooks(term, args)

            term.warning.assert_not_called()
            term.ok.assert_called_once_with(
                f"commitguard pre-commit hook installed at {tmpdir}/"
                ".git/hooks/pre-commit using pythonpath mode."
            )
