import ast
import checks
from helpers import Flake8ASTErrorInfo


class MCodingASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors: list[Flake8ASTErrorInfo] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):  # find all function nodes
        checks.LocalImportsNotAllowed.check_import_inside_function(node, self.errors)
        checks.UnconventionalFunctionNamesNotAllowed.check_function_name_camel_case(node, self.errors)
        checks.UnconventionalFunctionNamesNotAllowed.check_function_name_snake_case(node, self.errors)
        checks.UnconventionalFunctionNamesNotAllowed.check_first_word_in_function_name_is_verb(node, self.errors)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        checks.UnconventionalClassNamesNotAllowed.check_class_name_camel_case(node, self.errors)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        checks.UnconventionalVariableNamesNotAllowed.check_variable_name_plurality(node, self.errors)
        checks.UnconventionalVariableNamesNotAllowed.check_last_word_in_variable_name_is_noun(node, self.errors)
        checks.UnconventionalVariableNamesNotAllowed.check_variable_name_camel_case(node, self.errors)
        checks.UnconventionalVariableNamesNotAllowed.check_variable_name_snake_case(node, self.errors)
        self.generic_visit(node)


class ItzmaASTPlugin:

    name = "flake8_mcoding_ast"
    version = "0.1.1"

    def __init__(self, tree: ast.AST):
        self._tree = tree

    def run(self):
        visitor = MCodingASTVisitor()
        visitor.visit(self._tree)  # pass the root of the AST
        yield from visitor.errors
