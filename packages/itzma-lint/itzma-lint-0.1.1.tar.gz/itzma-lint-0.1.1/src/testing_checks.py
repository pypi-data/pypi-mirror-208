import ast
from typing import NamedTuple
from inflection import camelize, pluralize


class Flake8ASTErrorInfo(NamedTuple):
    line_number: int
    offset: int
    msg: str
    cls: type


class LocalImportsNotAllowed:
    msg = "IM local imports are not allowed inside a function"

    @classmethod
    def check(cls, node, errors):
        for child in ast.walk(node):
            if isinstance(child, (ast.Import, ast.ImportFrom)):
                err = Flake8ASTErrorInfo(child.lineno, child.col_offset, cls.msg, cls)
                errors.append(err)


class UnconventionalFunctionNamesNotAllowed:
    msg1 = "IM function names must be camel case with lowercase first letter"
    msg2 = "IM function names must start with a verb"

    @classmethod
    def check(cls, node, errors):
        for child in ast.walk(node):
            if isinstance(child, ast.FunctionDef):
                func_name = child.name
                # camelcase check:
                if not camelize(func_name, uppercase_first_letter=False) == func_name:
                    err = Flake8ASTErrorInfo(
                        child.lineno, child.col_offset, cls.msg1, cls
                    )
                    errors.append(err)


class UnconventionalClassNamesNotAllowed:
    msg = "IM class names must be camel case with uppercase first letter"

    @classmethod
    def check(cls, node, errors):
        for child in ast.walk(node):
            if isinstance(child, ast.ClassDef):
                class_name = child.name
                if not camelize(class_name, uppercase_first_letter=True) == class_name:
                    err = Flake8ASTErrorInfo(
                        child.lineno, child.col_offset, cls.msg, cls
                    )
                    errors.append(err)


class UnconventionalVariableNamesNotAllowed:
    msg = "IM variable names must be plural if they are assigned to a list"

    @classmethod
    def check(cls, node, errors):
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):  # check assignment
                if isinstance(child.value, ast.List):  # if the value is a list
                    if (
                        pluralize(child.targets[0].id) == child.targets[0].id
                    ):  # and the name is not plural
                        err = Flake8ASTErrorInfo(
                            child.lineno, child.col_offset, cls.msg, cls
                        )
                        errors.append(err)
