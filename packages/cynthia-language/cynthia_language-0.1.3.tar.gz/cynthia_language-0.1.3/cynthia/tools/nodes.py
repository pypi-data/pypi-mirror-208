"""AST node definitions for the Cynthia language."""

from abc import ABC
from dataclasses import dataclass
from decimal import Decimal
from typing import List

from cynthia.tools.lexer import Token, TokenType


@dataclass(kw_only=True)
class Node(ABC):
    """Class representing an AST node."""

    token: Token = None


@dataclass(kw_only=True)
class VariableNode(Node):
    """Variable node representation."""

    name: str | None = None

    def __post_init__(self):
        if self.name is None:
            self.name = self.token.value  # noqa: WPS601


@dataclass
class ProgramNode(Node):
    """ProgramNode representation.

    This node will be the root of the AST.
    """

    statements: List[Node]


@dataclass(kw_only=True)
class BinaryNode(Node):
    """BinaryNode representation."""

    left: Node
    right: Node


@dataclass(kw_only=True)
class AssignmentNode(Node):
    """Separate node for assignments."""

    token: Token = Token(TokenType.ASSIGN, '=')
    variable: VariableNode  # noqa: WPS110
    expression: Node


@dataclass(kw_only=True)
class UnaryNode(Node):
    """UnaryNode representation."""

    child: Node


@dataclass(kw_only=True)
class FunctionNode(VariableNode):
    """Function node representation."""

    args: list[Node]


@dataclass(kw_only=True)
class NumberNode(Node):
    """Number node representation."""

    amount: Decimal | None = None

    def __post_init__(self):
        """Set value."""
        if self.amount is None:
            self.amount = Decimal(self.token.value)  # noqa: WPS601
