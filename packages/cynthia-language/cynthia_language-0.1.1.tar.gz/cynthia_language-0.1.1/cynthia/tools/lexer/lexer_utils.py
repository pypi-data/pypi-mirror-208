"""Utility functions for the lexer module."""

from cynthia.tools.lexer.supported_tokens import TokenType, white_space_tokens


def is_white_space(token_type: TokenType) -> bool:
    return token_type in white_space_tokens
