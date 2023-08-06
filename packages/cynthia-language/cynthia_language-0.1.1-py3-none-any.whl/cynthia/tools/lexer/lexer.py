"""Cynthia language lexer definition."""

from typing import List

from cynthia.tools.lexer.lexer_utils import is_white_space
from cynthia.tools.lexer.logics import (
    CommentTokenLogic, IDNameTokenLogic, NumberTokenLogic, TextMatcherTokenLogic, TokenLogic,
)
from cynthia.tools.lexer.supported_tokens import TokenType
from cynthia.tools.lexer.tokens import Token


class UnsupportedTokenError(Exception):
    """Raised when the input wasn't fully processed."""


class Lexer(object):
    """The lexer's job is to make a token sequence for a given text input.

    Tokens will be created via the `token_create_logics`.

    The lexer will iterate through the list and the first logic that does not
    return None will be used.
    """

    token_create_logics: List[TokenLogic] = [
        TextMatcherTokenLogic(TokenType.PLUS, text_to_match='+'),
        TextMatcherTokenLogic(TokenType.MINUS, text_to_match='-'),
        TextMatcherTokenLogic(TokenType.ASTERISK, text_to_match='*'),
        TextMatcherTokenLogic(TokenType.FORWARD_SLASH, text_to_match='/'),
        TextMatcherTokenLogic(TokenType.ASSIGN, text_to_match='='),
        TextMatcherTokenLogic(TokenType.L_PAREN, text_to_match='('),
        TextMatcherTokenLogic(TokenType.R_PAREN, text_to_match=')'),
        TextMatcherTokenLogic(TokenType.COMMA, text_to_match=','),
        TextMatcherTokenLogic(TokenType.SPACE, text_to_match=' '),
        TextMatcherTokenLogic(TokenType.EOL, text_to_match='\n'),
        NumberTokenLogic(TokenType.INTEGER),
        IDNameTokenLogic(TokenType.ID),
        CommentTokenLogic(TokenType.COMMENT),
    ]

    def __init__(self, include_ws: bool = False):
        self.include_ws = include_ws

    def get_tokens(self, text: str) -> List[Token]:
        position = 0
        tokens = []

        token = self.get_next_token(text, position)
        while token:
            if self._check_white_space(token) and token.type != TokenType.COMMENT:
                tokens.append(token)
            position += len(token.value)
            token = self.get_next_token(text, position)

        if position + 1 < len(text):
            raise UnsupportedTokenError(f'Unsupported input starting with {text[position]}.')

        tokens.append(Token(TokenType.EOF, None))
        return tokens

    def get_next_token(self, text: str, position: int):
        for logic in self.token_create_logics:
            if token := logic.handle_input(text, position):
                return token
        return None

    def _check_white_space(self, token):
        return self.include_ws or not is_white_space(token.type)
