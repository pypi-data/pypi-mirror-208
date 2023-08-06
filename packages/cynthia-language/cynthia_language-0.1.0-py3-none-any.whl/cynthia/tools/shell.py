"""Shell application for the Cynthia language."""

from cynthia.tools.interpreter.interpreter import Interpreter


def run_shell():
    interpreter = Interpreter()
    while True:
        text = input('cynthia> ')

        if text == 'exit()':
            break

        try:
            interpreter.shell_interpret(text)
        except Exception as exc:
            print(exc)
