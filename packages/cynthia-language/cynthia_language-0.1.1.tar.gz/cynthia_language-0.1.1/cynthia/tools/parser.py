"""Cynthia language parser definition."""

from typing import Any, List

from cynthia.tools.lexer import Lexer, Token, TokenType
from cynthia.tools.nodes import (
    AssignmentNode, BinaryNode, FunctionNode, Node, NumberNode, ProgramNode, UnaryNode, VariableNode,
)


class Parser(object):
    """The parser creates the AST for a given token sequence."""

    def __init__(self, lexer: Lexer = None):
        self.lexer = lexer if lexer else Lexer()

    @property
    def current_token(self) -> Token:
        return self._get_token(offset=0)

    @property
    def next_token(self) -> Token:
        return self._get_token(offset=1)

    def parse(self, to_parse: str | List[Token]) -> ProgramNode:
        self._set_tokens(to_parse)
        try:
            return self.program()
        except Exception:
            raise SyntaxError('Syntax error.')

    def program(self) -> ProgramNode:
        """Get the root node of the program.

        program: statement_list EOF

        Returns:
            ProgramNode: root of the program
        """
        statements = self.statement_list()
        self.eat(TokenType.EOF)
        return ProgramNode(statements=statements)

    def statement_list(self) -> List[Node]:
        """Get each statement of the program.

        statement_list: statement | statement EOL statement_list

        Returns:
            List[StatementNode]: List of statements.
        """
        first_statement = self.statement()
        statements = [first_statement] if first_statement else []

        if self.current_token.type == TokenType.EOL:
            self.eat_current()
            statements.extend(self.statement_list())

        return statements

    def statement(self) -> Node:
        """Get a single statement.

        statement: assignment_statement | expr | EMPTY

        Returns:
            Node: Statement node.
        """
        if self._is_assignment():
            return self.assignment_statement()
        return self.expr()

    def assignment_statement(self) -> AssignmentNode:
        """Get assignment statement.

        assignment_statement: VARIABLE ASSIGN expr

        Returns:
            AssignmentNode: Assignment.
        """
        variable_node = VariableNode(token=self.eat(TokenType.ID))
        self.eat(TokenType.ASSIGN)
        return AssignmentNode(
            variable=variable_node,
            expression=self.expr(),
        )

    def expr(self) -> Node:
        """Get an expression.

        expr: term ((PLUS | MINUS) term)*

        Returns:
            Node: expression
        """
        node = self.term()
        while self.current_token.type in {TokenType.PLUS, TokenType.MINUS}:
            token = self.eat_current()
            if right := self.term():
                node = BinaryNode(left=node, token=token, right=right)
            else:
                self.error()
        return node

    def term(self) -> Node:
        """Get a term.

        term: factor ((MUL | DIV) factor)*

        Returns:
            Node: expression
        """
        node = self.factor()
        while self.current_token.type in {TokenType.ASTERISK, TokenType.FORWARD_SLASH}:
            token = self.eat_current()
            if right := self.factor():
                node = BinaryNode(left=node, token=token, right=right)
            else:
                self.error()
        return node

    def factor(self) -> Node:
        """Get a factor.

        factor
            : NUMBER
            | VARIABLE
            | L_PAREN expr R_PAREN
            | (PLUS|MINUS) expr
            | function_call
            ;

        Returns:
            Node: factor
        """
        token = self.current_token
        node = None

        match(token.type):
            case TokenType.INTEGER:
                node = NumberNode(token=self.eat_current())
            case TokenType.ID:
                if self.next_token.type == TokenType.L_PAREN:
                    node = self.function_call()
                else:
                    node = VariableNode(token=self.eat_current())
            case TokenType.L_PAREN:
                self.eat_current()
                node = self.expr()
                self.eat(TokenType.R_PAREN)
            case TokenType.MINUS | TokenType.PLUS:
                self.eat_current()
                node = UnaryNode(child=self.factor(), token=token)

        return node

    def function_call(self) -> FunctionNode:
        """Get a function call.

        function_call: ID L_PAREN args R_PAREN

        Returns:
            FunctionNode: function call.
        """
        id_token = self.eat_current()
        self.eat(TokenType.L_PAREN)
        args = self.args()
        self.eat(TokenType.R_PAREN)
        return FunctionNode(token=id_token, args=args)

    def args(self) -> List[Node]:
        """Get arguments.

        args: expr (COMMA expr)*

        Returns:
            List[Node]: list of arguments.
        """
        args = [self.expr()]
        while self.current_token.type == TokenType.COMMA:
            self.eat_current()
            if extra_arg := self.expr():
                args.append(extra_arg)
            else:
                self.error()
        return args

    def eat_current(self):
        if self.current_token:
            return self.eat(self.current_token.type)
        return None

    def eat(self, token_type: TokenType):
        if self.current_token.type == token_type:
            eaten_token = self.current_token
            self._pos += 1
            return eaten_token
        raise ValueError(
            'Tried to eat {expected_type} however next token was a {actual_type}'.format(
                expected_type=token_type,
                actual_type=self.current_token.type,
            ),
        )

    def _set_tokens(self, to_parse: str | List[Token]):
        self._pos = 0
        if isinstance(to_parse, str):
            self._tokens = self.lexer.get_tokens(to_parse)
        elif self._is_token_list(to_parse):
            self._tokens = to_parse
        else:
            raise ValueError('Only strings or list of tokens are supported.')

    def _is_assignment(self) -> bool:
        return (
            self.current_token.type == TokenType.ID and
            self.next_token.type == TokenType.ASSIGN
        )

    def _is_token_list(self, value_to_check: Any) -> bool:
        return isinstance(value_to_check, list) and self._each_element_is_token(value_to_check)

    def _each_element_is_token(self, list_to_check) -> bool:
        for token in list_to_check:
            if not isinstance(token, Token):
                return False
        return True

    def _get_token(self, offset: int) -> Token:
        try:
            return self._tokens[self._pos + offset]
        except (AttributeError, IndexError):
            return None
