"""testing csvsheet module."""

from typing import Union

import pytest

from csvsheet.csvsheet import main, run, sanitize_cell

__author__ = "Jesús Lázaro"
__copyright__ = "Jesús Lázaro"
__license__ = "MIT"


# create a fixture to test sanitize_cell
@pytest.mark.parametrize(
    ("cell", "expected"),
    [
        ("=1+1", 2),
        ("=1 + 1", 2),
        ("=1+1 # comment", 2),
        ("=1+1 # comment # comment", 2),
        ("=1+1 #", 2),
        ("=math.pi", 3.141592653589793),
        ("1+2", "1+2"),
        ("=int(1.0/2.0)", 0),
        ("=1+2", 3),
        pytest.param(
            '=import os; os.system("rm -rf /")',
            None,
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param("=1++", None, marks=pytest.mark.xfail(raises=SyntaxError)),
    ],
)
def test_sanitize_cell(
    cell: str,
    expected: Union[str, int, float],
):
    """Test sanitize_cell."""
    assert sanitize_cell(cell) == expected


# parametrize the main function
@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (
            ["tests/test_a.csv"],
            'item,a,b\r\nq,7,3+4\r\nw,21.0,0.75\r\nrtert,81.0,6\r\n"circle,area",18,m2\r\n',
        ),
        (
            ["tests/test_a.csv", "-o", "tests/test_a.csv.out"],
            "",
        ),
        (
            ["tests/test_a.ssv", "-o", "-", "-d", ";", "-q", "'", "-m", "@"],
            "item;a;b\r\nq;7;3+4\r\nw;21.0;0.75\r\nrtert;81.0;6\r\ncircle,area;18;m2\r\n",
        ),
        pytest.param(
            ["input.csv", "-o", "output.csv"],
            "argument INPUT_FILE: can't open 'input.csv'",
            marks=pytest.mark.xfail(raises=SystemExit),
        ),
        pytest.param(
            ["tests/test_b.csv", "-o", "-"],
            "Error: formula contains invalid characters",
            marks=pytest.mark.xfail(raises=SystemExit),
        ),
        pytest.param(
            ["tests/test_c.csv", "-o", "-"],
            "unexpected EOF while parsing",
            marks=pytest.mark.xfail(raises=SystemExit),
        ),
        pytest.param(
            ["-o", "output.csv"],
            "error: the following arguments are required: INPUT_FILE",
            marks=pytest.mark.xfail(raises=SystemExit),
        ),
        pytest.param(
            [],
            "usage:",
            marks=pytest.mark.xfail(raises=SystemExit),
        ),
    ],
)
def test_main(capsys, args, expected):
    """CLI Tests, happy path."""
    main(args)
    captured = capsys.readouterr()
    assert captured.out == expected


def test_simple_run():
    """Test run entry point."""
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2
