"""Cynthia language interpreter definition."""

import re
from decimal import Decimal
from io import TextIOBase

from cynthia.tools.interpreter.exceptions import (
    FunctionDoesNotExistError, InvalidGlobalVariableError, VariableDoesNotExitError, VisitorDoesNotExistError,
)
from cynthia.tools.lexer.supported_tokens import TokenType
from cynthia.tools.nodes import (
    AssignmentNode, BinaryNode, FunctionNode, Node, NumberNode, ProgramNode, UnaryNode, VariableNode,
)
from cynthia.tools.parser import Parser


class NodeVisitor(object):
    """Visitor pattern for nodes."""

    def visit(self, node: Node):
        method_name = 'visit_{node_name}'.format(
            node_name=self._pascal_to_snake(type(node).__name__),
        )
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise VisitorDoesNotExistError(f'Visitor does not exit for node {node}.')

    def _pascal_to_snake(self, pascal_name: str) -> str:
        return re.sub('(?<!^)(?=[A-Z])', '_', pascal_name).lower()


class Interpreter(NodeVisitor):
    """Interpreter will evaluate a given AST."""

    supported_file_extensions = ['cynthia']

    binary_logics = {
        TokenType.PLUS: lambda left, right: left + right,
        TokenType.MINUS: lambda left, right: left - right,
        TokenType.ASTERISK: lambda left, right: left * right,
        TokenType.FORWARD_SLASH: lambda left, right: left / right,
    }

    unary_logics = {
        TokenType.PLUS: lambda child: child,
        TokenType.MINUS: lambda child: -child,
    }

    core_functions = {
        'max': lambda *args: max(*args),
        'min': lambda *args: min(*args),
        'print': lambda *args: print(*args),
    }

    def __init__(self, parser: Parser = None, global_variables: dict = None):
        self.parser = parser if parser else Parser()
        self.global_variables = global_variables if global_variables else {}
        self._cast_global_variables()

    def visit_program_node(self, node: ProgramNode):
        for statement in node.statements:
            self.visit(statement)

    def visit_binary_node(self, node: BinaryNode):
        if binary_logic := self.binary_logics.get(node.token.type):
            return binary_logic(self.visit(node.left), self.visit(node.right))
        return None

    def visit_assignment_node(self, node: AssignmentNode):
        self.global_variables[node.variable.name] = self.visit(node.expression)

    def visit_unary_node(self, node: UnaryNode):
        if unary_logic := self.unary_logics.get(node.token.type):
            return unary_logic(node.child)
        return None

    def visit_number_node(self, number: NumberNode):
        return number.amount

    def visit_variable_node(self, variable_node: VariableNode):
        try:
            return self.global_variables[variable_node.name]
        except KeyError:
            raise VariableDoesNotExitError(f' Variable {variable_node.name} does not exist.')

    def visit_function_node(self, function_node: FunctionNode):
        if core_function := self.core_functions.get(function_node.token.value):
            args = [self.visit(arg) for arg in function_node.args]
            return core_function(*args)
        raise FunctionDoesNotExistError(f' Function {function_node.name} does not exist.')

    def interpret(self, to_interpret: str | Node | TextIOBase):
        if isinstance(to_interpret, TextIOBase):
            self._check_file_extension(to_interpret)
            to_interpret = to_interpret.read()
        if isinstance(to_interpret, str):
            to_interpret = self.parser.parse(to_interpret)
        return self.visit(to_interpret)

    def shell_interpret(self, to_interpret: str):
        print_interpret = f'print({to_interpret})\n'
        try:
            to_interpret = self.parser.parse(print_interpret)
        except Exception:
            to_interpret = self.parser.parse(to_interpret)
        self.interpret(to_interpret)

    def __getitem__(self, variable_name):
        return self.global_variables.get(variable_name)

    def _check_file_extension(self, input_file: TextIOBase):
        if input_file.name.split('.')[-1] not in self.supported_file_extensions:
            raise TypeError(
                'Allowed file extensions are: {extensions}'.format(
                    extensions=self.supported_file_extensions,
                ),
            )

    def _cast_global_variables(self):
        casted_global = {}
        for variable_name, variable_value in self.global_variables.items():
            try:
                casted_global[variable_name] = Decimal(variable_value)
            except Exception:
                raise InvalidGlobalVariableError(
                    'Global variable "{name}" has an invalid type "{type}"'.format(
                        name=variable_name,
                        type=type(variable_value).__name__,
                    ),
                )
        self.global_variables = casted_global
