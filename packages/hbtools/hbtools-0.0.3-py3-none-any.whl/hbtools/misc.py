"""Module providing miscellaneous functions related to printing."""
import sys
from shutil import get_terminal_size


def yes_no_prompt(question: str, *, default: bool = True) -> bool:
    """Prompts the user for a binary answer.

    Args:
        question: The text that will be shown to the user.
        default: Default value to use if the user just presses enter.

    Returns:
        True for yes, False for no
    """
    choices = " [Y/n]: " if default else " [y/N]: "

    while answer := input(question + choices).lower().strip():
        if answer not in ("y", "n"):
            print("Input invalid, please enter 'y' or 'n'")
            continue
        return answer == "y"

    return default


def clean_print(msg: str, fallback: tuple[int, int] = (156, 38), end: str = "\n") -> None:
    r"""Print the given string to the console and erase any character previously written on the line.

    Args:
        msg: String to print to the console.
        fallback: If using Windows, size of the terminal to use if it cannot be determined by shutil.
        end: What to add at the end of the print. Usually '\n' (new line), or '\r' (back to the start of the line).
    """
    if sys.platform != "win32":
        print("\033[2K" + msg, end=end, flush=True)
    else:
        print(msg + " " * (get_terminal_size(fallback=fallback).columns - len(msg)), end=end, flush=True)
