import sys
from contextlib import redirect_stdout, suppress
from io import StringIO

import hbtools
import pytest


@pytest.mark.parametrize(("msg", "expected"),
                         [("test1", "INFO - test1\n"),
                          ("test2", "INFO - test2\n"),
                          ])
def test_logger(msg: str, expected: str) -> None:
    logger = hbtools.create_logger("Test", log_dir=None, stdout=True, verbose_level="info")
    with redirect_stdout(StringIO()) as stdout:
        logger.handlers[0].stream = sys.stdout  # pyright: ignore[reportGeneralTypeIssues]
        logger.info(msg)
        logger.debug("Should not appear")
        logger.handlers[0].flush()
    assert stdout.getvalue() == expected


@pytest.mark.parametrize(("msg", "end", "expected"),
                         [("test1", "\n", "\x1b[2Ktest1\n"),
                          ("test2", "\r", "\x1b[2Ktest2\r"),
                          ])
def test_clean_print_linux(msg: str, end: str, expected: str) -> None:
    with redirect_stdout(StringIO()) as stdout:
        hbtools.clean_print(msg, end=end)
    assert stdout.getvalue() == expected


@pytest.mark.parametrize(("msg", "end", "expected"),
                         [("test1", "\n", "test1\n"),
                          ("test2", "\r", "test2\r"),
                          ])
def test_clean_print_windows(monkeypatch: pytest.MonkeyPatch, msg: str, end: str, expected: str) -> None:
    monkeypatch.setattr("sys.platform", "win32")
    with redirect_stdout(StringIO()) as stdout:
        hbtools.clean_print(msg, end=end)
    output = stdout.getvalue().replace(" ", "")
    assert output == expected


@pytest.mark.parametrize(("question", "default", "expected_answer"),
                         [("Question 1", "Y", True),
                          ("Question 2", "N", False),
                          ])
def test_yes_no(monkeypatch: pytest.MonkeyPatch, question: str, default: str, expected_answer: bool) -> None:
    def return_default(_: object) -> str:
        return default

    monkeypatch.setattr("builtins.input", return_default)
    answer = hbtools.yes_no_prompt(question)
    assert answer == expected_answer


def test_show_img() -> None:
    with suppress(AttributeError):
        hbtools.show_img(1)  # pyright: ignore[reportGeneralTypeIssues]
