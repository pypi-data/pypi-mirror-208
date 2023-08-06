import random
import dace

from typing import List, Dict

from daisy.random.randutils import DTYPES


def unary(operand: str, dtype) -> str:
    if dtype == dace.bool:
        expr = unary_logical(operand)
    elif DTYPES.index(dtype) >= DTYPES.index(dace.float32) and random.random() < 0.5:
        expr = unary_float_function(operand)
    else:
        expr = unary_arithmetic(operand)

    return expr


def binary(left_operand: str, right_operand: str, dtype) -> str:
    if dtype == dace.bool:
        expr = binary_logical(left_operand, right_operand)
    elif random.random() < 0.2:
        expr = binary_float_function(left_operand, right_operand)
    else:
        expr = binary_arithmetic(left_operand, right_operand)

    return expr


def unary_arithmetic(operand: str) -> str:
    right_operand = str(random.randint(1, 256))
    expr = binary_arithmetic(left_operand=operand, right_operand=right_operand)
    return expr


def unary_conditional(operand: str) -> str:
    right_operand = str(random.randint(-256, 256))
    expr = binary_conditional(left_operand=operand, right_operand=right_operand)
    return expr


def unary_logical(operand: str) -> str:
    dice = random.random()
    if dice < 0.1:
        op = "not"
        expr = f"""{op} {operand}"""
    else:
        bool_operands = ["True", "False"]
        right_operand = random.choice(bool_operands)
        expr = binary_logical(left_operand=operand, right_operand=right_operand)

    return expr


def unary_float_function(operand: str) -> str:
    ops = (
        "sin",
        "cos",
        "tan",
        "sinh",
        "cosh",
        "tanh",
        "exp",
    )
    op = random.choice(ops)

    expr = f"""{op}({operand})"""
    return expr


def binary_arithmetic(left_operand: str, right_operand: str) -> str:
    funcs = ("min", "max")
    ops = ("+", "-", "*", "/")
    op = random.choice(ops)

    if random.random() < 0.33:
        op = random.choice(funcs)
        expr = f"""{op}({left_operand}, {right_operand})"""
        return expr
    else:
        op = random.choice(ops)
        expr = f"""{left_operand} {op} {right_operand}"""

    return expr


def binary_conditional(left_operand: str, right_operand: str) -> str:
    ops = (
        "<",
        ">",
        "<=",
        ">=",
        "==",
        "!=",
    )
    op = random.choice(ops)
    expr = f"""{left_operand} {op} {right_operand}"""
    return expr


def binary_logical(left_operand: str, right_operand: str) -> str:
    ops = ("and", "or")
    op = random.choice(ops)

    expr = f"""{left_operand} {op} {right_operand}"""
    return expr


def binary_float_function(left_operand: str, right_operand: str) -> str:
    ops = ("pow",)
    op = random.choice(ops)

    expr = f"""{op}({left_operand}, {right_operand})"""
    return expr


def aggregate(accesses: Dict[str, dace.Memlet], dtype) -> str:
    if dtype == dace.bool:
        ops = ("and", "or")
    else:
        ops = ("+", "-", "*")

    items = list(accesses.items())
    if len(items) == 1:
        expr = unary(items[0][0], dtype=dtype)
    else:
        expr = items[0][0]
        for identifier, memlet in items[1:]:
            op = random.choice(ops)
            expr += f" {op} {identifier}"

    return expr
