"""Interpreter related exceptions."""


class InterpreterError(Exception):
    """Base class for interpreter related exceptions."""


class VisitorDoesNotExistError(InterpreterError):
    """Exception when no visitor does not exist."""


class VariableDoesNotExitError(InterpreterError):
    """Exception when variable does not exist."""


class FunctionDoesNotExistError(InterpreterError):
    """Exception when function does not exist."""


class InvalidGlobalVariableError(InterpreterError):
    """Exception when invalid typed global variable was passed."""
