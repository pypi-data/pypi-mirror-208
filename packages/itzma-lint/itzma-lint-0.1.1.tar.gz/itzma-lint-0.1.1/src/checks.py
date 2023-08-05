import ast
from typing import NamedTuple
import re
from inflection import camelize, pluralize
import nltk
from nltk.corpus import brown
from collections import Counter, defaultdict

nltk.download("brown")


word_tags = defaultdict(list)
for word, pos in brown.tagged_words():
    if pos not in word_tags[word]:  # to append one tag only once
        word_tags[word].append(pos)  # adding key-value to x


VERB_CODES = [
    "VB",  # Verb, base form
    "VBD",  # Verb, past tense
    "VBG",  # Verb, gerund or present participle
    "VBN",  # Verb, past participle
    "VBP",  # Verb, non-3rd person singular present
    "VBZ",  # Verb, 3rd person singular present
]


class Flake8ASTErrorInfo(NamedTuple):
    line_number: int
    offset: int
    msg: str
    cls: type


class LocalImportsNotAllowed:
    msg = "IM local imports are not allowed inside a function"

    @classmethod
    def check(cls, node: ast.FunctionDef, errors: list[Flake8ASTErrorInfo]) -> None:
        for child in ast.walk(node):
            if isinstance(child, (ast.Import, ast.ImportFrom)):
                err = Flake8ASTErrorInfo(child.lineno, child.col_offset, cls.msg, cls)
                errors.append(err)


class UnconventionalFunctionNamesNotAllowed:
    msg1 = "IM function names must be camel case with lowercase first letter"
    msg2 = "IM function names must start with a verb"

    @classmethod
    def check(cls, node: ast.FunctionDef, errors: list[Flake8ASTErrorInfo]) -> None:
        for child in ast.walk(node):
            if isinstance(child, ast.FunctionDef):
                func_name = child.name
                # camelcase check:
                if not camelize(func_name, uppercase_first_letter=False) == func_name:
                    err = Flake8ASTErrorInfo(
                        child.lineno, child.col_offset, cls.msg1, cls
                    )
                    errors.append(err)

    @classmethod
    def checkFirstWordIsVerb(
        cls, node: ast.FunctionDef, errors: list[Flake8ASTErrorInfo]
    ) -> None:
        for child in ast.walk(node):
            if isinstance(child, ast.FunctionDef):
                func_name = child.name
                # camelcase check:
                if not camelize(func_name, uppercase_first_letter=False) == func_name:
                    continue
                reformatted = re.sub(
                    "([A-Z][a-z]+)", r" \1", re.sub("([A-Z]+)", r" \1", func_name)
                ).split()
                first_word = reformatted[0]
                first_word_pos = word_tags[first_word]
                if first_word_pos not in VERB_CODES:
                    err = Flake8ASTErrorInfo(
                        child.lineno, child.col_offset, cls.msg2, cls
                    )
                    errors.append(err)


class UnconventionalClassNamesNotAllowed:
    msg = "IM class names must be camel case with uppercase first letter"

    @classmethod
    def check(cls, node: ast.ClassDef, errors: list[Flake8ASTErrorInfo]) -> None:
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
    def check(cls, node: ast.FunctionDef, errors: list[Flake8ASTErrorInfo]) -> None:
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
