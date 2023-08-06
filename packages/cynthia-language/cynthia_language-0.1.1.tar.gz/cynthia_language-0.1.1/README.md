# Cynthia script language

Cynthia is a small interpreted script language for basic mathematical expressions written in python.

## The language currently supports:

 - the four fundamental operations of arithmetic (**addition**, **subtraction**, **multiplication**, **division**)
 - **parentheses** which can modify the order of operations.
 - **variables** and **variable assignments**
 - a number of **built-in** functions


## Built-in functions:

### `min(*args) -> number`

Returns the minimum value of the arguments.


### `max(*args) -> number`

Returns the maximum value of the arguments.

### `print(*args)`

Prints the arguments to the standard output.


# Installation

`pip install cynthia-language`

# Usage

## shell enviroment

Cynthia language can be run in a **shell enviroment** where each expression
will be evaluated and printed out to the standard output.

```
$: python -m cynthia
cynthia> 3 * (5 + 2) / 4
5.25
cynthia> x = 3 * 3
cynthia> 4 * x - 5
31
```

## executing `.cynthia` files

Cynthia language code can be written in `.cynthia` files:

```
# example.cynthia file

# you can write comments
a = 1
b = 2
c = a + b * 3

result = min(a, b, c)

print(result)
```

Which can be executed with the interpreter:

`python -m cynthia example.cynthia`

# CFG for the syntax

```
program
    : statement_list EOF
    ;

statement_list
    : statement
    | statement EOL statement_list
    ;

statement
    : assignment_statement
    | expr
    | EMPTY
    ;

assignment_statement
    : VARIABLE ASSIGN expr
    ;

expr
    : term
    | term PLUS expr
    | term MINUS expr
    :

term
    : factor
    | factor MUL term
    | factor DIV term
    ;

factor
    : NUMBER
    | VARIABLE
    | L_PAREN expr R_PAREN
    | PLUS expr
    | MINUS expr
    | function_call
    ;

function_call
    : ID L_PAREN args R_PAREN
    ;

args
    : expr
    | expr COMMA args
    ;
```

# Use the language tools directly

Language tools can be used directly.

```
from cynthia.tools import Parser

parser = Parser()
parser.parse('x=1+2')

parser['x']
# 3
```