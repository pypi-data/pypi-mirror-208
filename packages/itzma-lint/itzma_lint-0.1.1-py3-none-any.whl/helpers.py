from typing import NamedTuple


class Flake8ASTErrorInfo(NamedTuple):
    line_number: int
    offset: int
    msg: str
    cls: type
