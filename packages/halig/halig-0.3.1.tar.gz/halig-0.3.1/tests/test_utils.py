from typing import Callable

import pytest

from halig.utils import capture


def exec_capture(func: Callable):
    return capture(func)()


def test_capture():
    def func(): return 1

    assert exec_capture(func) == 1


def test_capture_exits_with_custom_os_error(mocker):
    exit_code = None

    def mock_exit(code):
        nonlocal exit_code
        exit_code = code

    mocker.patch('halig.utils.sys.exit', side_effect=mock_exit)

    def func(): raise OSError(2, "os_error_func")

    exec_capture(func)
    assert exit_code == 2


def test_capture_exits_with_os_error(mocker):
    exit_code = None

    def mock_exit(code):
        nonlocal exit_code
        exit_code = code

    mocker.patch('halig.utils.sys.exit', side_effect=mock_exit)

    def func(): raise OSError

    exec_capture(func)
    assert not exit_code


def test_capture_exits_with_value_error(mocker):
    exit_code = None

    def mock_exit(code):
        nonlocal exit_code
        exit_code = code

    mocker.patch('halig.utils.sys.exit', side_effect=mock_exit)

    def func(): raise ValueError("value_error_func")

    exec_capture(func)
    assert exit_code == 1


def test_capture_exits_with_other_error(mocker):
    exit_code = None

    def mock_exit(code):
        nonlocal exit_code
        exit_code = code

    mocker.patch('halig.utils.sys.exit', side_effect=mock_exit)

    def func(): raise ArithmeticError("arithmetic_error_func")

    exec_capture(func)
    assert exit_code == 2
