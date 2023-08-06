"""Supported tokens for the Cynthia language."""

from enum import Enum


class TokenType(Enum):
    """Supported token types."""

    NUMBER = 'NUMBER'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    ASTERISK = 'ASTERISK'
    FORWARD_SLASH = 'FORWARD_SLASH'
    L_PAREN = 'L_PAREN'
    R_PAREN = 'R_PAREN'
    ASSIGN = 'ASSIGN'
    ID = 'ID'
    EOF = 'EOF'
    EOL = 'EOL'
    SPACE = 'SPACE'
    COMMA = 'COMMA'
    COMMENT = 'COMMENT'


white_space_tokens = [
    TokenType.SPACE,
]
