from typing import Optional

from rich.progress import BarColumn
from rich.progress import Progress as RichProgress
from rich.progress import SpinnerColumn, TaskProgressColumn, TextColumn

from commitguard.extension.rich import RichTerminal as Terminal
from commitguard.extension.terminal import Signs

from .helper import deprecated

__all__ = (
    "Terminal",
    "Progress",
    "Signs",
    "bold_info",
    "error",
    "fail",
    "info",
    "ok",
    "out",
    "warning",
)

__term = Terminal()


def ok(message: str) -> None:
    """
    Highlight message as a success/ok in the terminal

    Args:
        message: Message to print
    """
    __term.ok(message)


def fail(message: str) -> None:
    """
    Highlight message as a failure in the terminal

    Args:
        message: Message to print
    """
    __term.fail(message)


def error(message: str) -> None:
    """
    Highlight message as an error in the terminal

    Args:
        message: Message to print
    """
    __term.error(message)


def warning(message: str) -> None:
    """
    Highlight message as a warning in the terminal

    Args:
        message: Message to print
    """
    __term.warning(message)


def info(message: str) -> None:
    """
    Highlight message as an information in the terminal

    Args:
        message: Message to print
    """
    __term.info(message)


def bold_info(message: str) -> None:
    """
    Highlight message as an strong information in the terminal

    Args:
        message: Message to print
    """
    __term.bold_info(message)


def out(message: str):
    """
    Print message to the terminal without highlighting

    Args:
        message: Message to print
    """
    __term.out(message)


@deprecated
def overwrite(message: str, new_line: bool = False):
    pass


def _set_terminal(term: Optional[Terminal] = None) -> Terminal:
    global __term
    __term = term or Terminal()
    return __term


class Progress(RichProgress):
    def __init__(self, terminal: Terminal) -> None:
        super().__init__(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=terminal._console,
            transient=True,
        )

    def finish_task(self, task_id):
        self.update(task_id, total=1, advance=1)

    def __enter__(
        self,
    ) -> "Progress":
        return super().__enter__()  # type: ignore
