import ast
import checks
from helpers import Flake8ASTErrorInfo


class MCodingASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors: list[Flake8ASTErrorInfo] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):  # find all function nodes
        checks.LocalImportsNotAllowed.check(node, self.errors)
        checks.UnconventionalFunctionNamesNotAllowed.check(node, self.errors)
        checks.UnconventionalFunctionNamesNotAllowed.checkFirstWordIsVerb(
            node, self.errors
        )
        checks.UnconventionalVariableNamesNotAllowed.check(node, self.errors)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        checks.UnconventionalClassNamesNotAllowed.check(node, self.errors)
        self.generic_visit(node)


class ItzmaASTPlugin:

    name = "flake8_mcoding_ast"
    version = "0.0.0"

    def __init__(self, tree: ast.AST):
        self._tree = tree

    def run(self):
        visitor = MCodingASTVisitor()
        visitor.visit(self._tree)  # pass the root of the AST
        yield from visitor.errors
