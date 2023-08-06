import ast
import re
from inflection import camelize, pluralize
import helpers


class LocalImportsNotAllowed:
    msg = "IMB01 local imports are not allowed inside a function"

    @classmethod
    def check_import_inside_function(cls, node: ast.FunctionDef, errors: list[helpers.Flake8ASTErrorInfo]) -> None:
        """
        Check if there's an import inside a function

        Args:
            node: ast.FunctionDef
            errors: a list of errors found
        """
        for child in ast.walk(node):
            if isinstance(child, (ast.Import, ast.ImportFrom)):
                err = helpers.Flake8ASTErrorInfo(child.lineno, child.col_offset, cls.msg, cls)
                errors.append(err)


class UnconventionalFunctionNamesNotAllowed:
    msg1 = "IMC01 function names must be camel case with lowercase first letter"
    msg2 = "IMB02 function names must start with a verb"
    msg3 = "IMS01 function names must be snake case with lowercase first letter"

    @classmethod
    def check_function_name_camel_case(cls, node: ast.FunctionDef, errors: list[helpers.Flake8ASTErrorInfo]) -> None:
        """
        Check if a function name is a de-capitalized camel case

        Args:
            node: ast.FunctionDef
            errors: a list of errors found
        """
        for child in ast.walk(node):
            if isinstance(child, ast.FunctionDef):
                func_name = child.name
                # camelcase check:
                if not camelize(func_name, uppercase_first_letter=False) == func_name:
                    err = helpers.Flake8ASTErrorInfo(child.lineno, child.col_offset, cls.msg1, cls)
                    errors.append(err)

    @classmethod
    def check_function_name_snake_case(cls, node: ast.FunctionDef, errors: list[helpers.Flake8ASTErrorInfo]) -> None:
        """
        Check if a function name is a snake case

        Args:
            node: ast.FunctionDef
            errors: a list of errors found
        """
        for child in ast.walk(node):
            if isinstance(child, ast.FunctionDef):
                func_name = child.name
                # snake case check:
                if not func_name.islower():
                    err = helpers.Flake8ASTErrorInfo(child.lineno, child.col_offset, cls.msg3, cls)
                    errors.append(err)

    @classmethod
    def check_first_word_in_function_name_is_verb(
        cls, node: ast.FunctionDef, errors: list[helpers.Flake8ASTErrorInfo]
    ) -> None:
        """
        Check if the first word in the function name is a verb

        Args:
            node: ast.FunctionDef
            errors: a list of errors found
        """
        for child in ast.walk(node):
            if isinstance(child, ast.FunctionDef):
                func_name = child.name
                # camelcase check:
                if not camelize(func_name, uppercase_first_letter=False) == func_name:
                    continue
                reformatted = re.sub("([A-Z][a-z]+)", r" \1", re.sub("([A-Z]+)", r" \1", func_name)).split()
                first_word = reformatted[0]
                if (
                    len(helpers.word_tags[first_word]) == 0
                    or helpers.word_tags[first_word][0] not in helpers.NOUN_CODES
                ):
                    err = helpers.Flake8ASTErrorInfo(child.lineno, child.col_offset, cls.msg2, cls)
                    errors.append(err)


class UnconventionalClassNamesNotAllowed:
    msg = "IMC02 class names must be camel case with uppercase first letter"

    @classmethod
    def check_class_name_camel_case(cls, node: ast.ClassDef, errors: list[helpers.Flake8ASTErrorInfo]) -> None:
        """
        Check if a class name is a capitalized camel case

        Args:
            node: ast.ClassDef
            errors: a list of errors found
        """
        for child in ast.walk(node):
            if isinstance(child, ast.ClassDef):
                class_name = child.name
                if not camelize(class_name, uppercase_first_letter=True) == class_name:
                    err = helpers.Flake8ASTErrorInfo(child.lineno, child.col_offset, cls.msg, cls)
                    errors.append(err)


class UnconventionalVariableNamesNotAllowed:
    msg1 = "IMB03 variable names must be plural if they are assigned to a list"
    msg2 = "IMB04 variable names must be nouns"
    msg3 = "IMC03 variable names must be camel case with lowercase first letter"
    msg4 = "IMS02 variable names must be snake case with lowercase first letter"

    @classmethod
    def check_variable_name_plurality(cls, node: ast.Assign, errors: list[helpers.Flake8ASTErrorInfo]) -> None:
        """
        Check if a variable name assigned to a list is plural

        Args:
            node: ast.FunctionDef
            errors: a list of errors found
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):  # check assignment
                if isinstance(child.value, ast.List):  # if the value is a list or set
                    if pluralize(child.targets[0].id) == child.targets[0].id:  # and the name is not plural
                        err = helpers.Flake8ASTErrorInfo(child.lineno, child.col_offset, cls.msg1, cls)
                        errors.append(err)

    @classmethod
    def check_last_word_in_variable_name_is_noun(
        cls, node: ast.Assign, errors: list[helpers.Flake8ASTErrorInfo]
    ) -> None:
        """
        Check if the last word in the variable name is a noun

        Args:
            node: ast.FunctionDef
            errors: a list of errors found
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                func_name = child.targets[0].id
                # camelcase check:
                if not camelize(func_name, uppercase_first_letter=False) == func_name:
                    continue
                reformatted = re.sub("([A-Z][a-z]+)", r" \1", re.sub("([A-Z]+)", r" \1", func_name)).split()
                last_word = reformatted[-1]
                if len(helpers.word_tags[last_word]) == 0 or helpers.word_tags[last_word][0] not in helpers.NOUN_CODES:
                    err = helpers.Flake8ASTErrorInfo(child.lineno, child.col_offset, cls.msg2, cls)
                    errors.append(err)

    @classmethod
    def check_variable_name_camel_case(cls, node: ast.Assign, errors: list[helpers.Flake8ASTErrorInfo]) -> None:
        """
        Check if a function name is a de-capitalized camel case

        Args:
            node: ast.FunctionDef
            errors: a list of errors found
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                func_name = child.targets[0].id
                # camelcase check:
                if not camelize(func_name, uppercase_first_letter=False) == func_name:
                    err = helpers.Flake8ASTErrorInfo(child.lineno, child.col_offset, cls.msg3, cls)
                    errors.append(err)

    @classmethod
    def check_variable_name_snake_case(cls, node: ast.Assign, errors: list[helpers.Flake8ASTErrorInfo]) -> None:
        """
        Check if a function name is a snake case

        Args:
            node: ast.FunctionDef
            errors: a list of errors found
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                func_name = child.targets[0].id
                # snake case check:
                if not func_name.islower():
                    err = helpers.Flake8ASTErrorInfo(child.lineno, child.col_offset, cls.msg4, cls)
                    errors.append(err)
