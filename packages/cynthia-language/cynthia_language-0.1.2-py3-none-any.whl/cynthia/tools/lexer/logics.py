"""Logic definitions for token creation."""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from functools import wraps
from string import ascii_letters, digits, printable

from cynthia.tools.lexer.tokens import Token


def set_text_and_pos(handle_input):
    @wraps(handle_input)
    def wrapper(self, input_txt: str, pos: int):
        self._text = input_txt
        self._pos = pos
        return handle_input(self, input_txt, pos)
    return wrapper


class TokenLogic(ABC):
    """Class representing token creating logic.

    TokenLogics will handle token creation for given text with a given
    position.

    The `handle_input` method should return the created Token and the number
    of consumed characters from the text.

    The TokenLogic can not create a Token it should return None.
    """

    def __init__(self, token_type: Enum):
        self.token_type = token_type

    @abstractmethod
    def handle_input(self, input_txt: str, pos: int) -> Token | None:
        """Handle input for with given position.

        Args:
            input_txt (str): Complete input text.
            pos (int): Current position.

        Returns:
            Token | None: Token if created else None.
        """

    @property
    def current_char(self) -> str:
        try:
            return self._text[self._pos]
        except (IndexError):
            return None
        except AttributeError:
            logging.warning('_text was not set! Use the `set_text_and_pos` decorator.')

    def advance(self):
        try:
            self._pos += 1
        except AttributeError:
            logging.warning('_pos was not set! Use the `set_text_and_pos` decorator.')


class TextMatcherTokenLogic(TokenLogic):
    """Token logic for matching entire texts."""

    def __init__(self, *args, text_to_match: str, **kwargs):
        super().__init__(*args, **kwargs)
        self._text_to_match = text_to_match

    @set_text_and_pos
    def handle_input(self, input_txt: str, pos: int) -> Token:
        received_text = self._get_sub_text(input_txt, pos)
        if received_text and received_text == self._text_to_match:
            return Token(self.token_type, received_text)
        return None

    def _get_sub_text(self, text: str, pos: int) -> str:
        slice_until = pos + len(self._text_to_match)
        try:
            return text[pos:slice_until]
        except IndexError:
            return None


class PatternMatcherTokenLogic(TokenLogic):
    """Token logic for matching patterns."""

    supported_first_chars: str
    supported_chars: str

    @set_text_and_pos
    def handle_input(self, input_txt: str, pos: int) -> Token:
        text_matched = ''

        if self.current_char is None or self.current_char not in self.supported_first_chars:
            return None

        while self.current_char and self.current_char in self.supported_chars:
            text_matched += self.current_char
            self.advance()

        return Token(self.token_type, text_matched) if text_matched else None


class IDNameTokenLogic(PatternMatcherTokenLogic):
    """Token logic for ID names.

    ID names will be used for variable names and function names.

    ID names can contain lowercase and uppercase letters digits and the
    underscore character. ID names first letter can not be a digit.
    """

    supported_first_chars = ascii_letters
    supported_chars = f'{ascii_letters}{digits}_'


class NumberTokenLogic(PatternMatcherTokenLogic):
    """Token logic for numbers."""

    supported_first_chars = digits
    supported_chars = f'{digits}.'

    def handle_input(self, input_txt: str, pos: int) -> Token:
        token = super().handle_input(input_txt, pos)
        if token is not None and self._dot_placement_correct(token.value):
            return token
        return None

    def _dot_placement_correct(self, number_text: str) -> bool:
        return not number_text.endswith('.') and number_text.count('.') <= 1


class CommentTokenLogic(PatternMatcherTokenLogic):
    """Token logic for comments."""

    supported_first_chars = '#'
    supported_chars = printable.replace('\n', '')
