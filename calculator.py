"""Calculator module providing arithmetic operations via a switch statement (match/case).

This module defines the `calculate` function used as a tool by the AI chatbot,
as well as the tool schema definition for OpenAI-compatible function calling.
"""

from typing import Any, Union


def calculate(operation: str, a: Union[float, int, str], b: Union[float, int, str]) -> Union[float, int, str]:
    """Perform basic arithmetic calculations using Python's match/case switch statement.

    Args:
        operation: The arithmetic operation to execute (e.g. 'add', 'subtract',
          'multiply', 'divide', 'power', 'modulo').
        a: The first operand (left-hand side).
        b: The second operand (right-hand side).

    Returns:
        The computed result (as int or float), or an error string if invalid.
    """
    # Safely convert operands to float
    try:
        num_a = float(a)
        num_b = float(b)
    except (ValueError, TypeError):
        return f"Error: Invalid operands provided. 'a'={a}, 'b'={b} must be numbers."

    op = str(operation).strip().lower()

    # Switch statement using Python match-case
    match op:
        case "add" | "+" | "addition" | "plus" | "sum":
            result = num_a + num_b

        case "subtract" | "-" | "subtraction" | "minus" | "diff":
            result = num_a - num_b

        case "multiply" | "*" | "multiplication" | "times" | "product":
            result = num_a * num_b

        case "divide" | "/" | "division":
            if num_b == 0:
                return "Error: Division by zero is not allowed."
            result = num_a / num_b

        case "power" | "**" | "^" | "pow" | "exponent":
            try:
                result = num_a ** num_b
            except OverflowError:
                return "Error: Calculation resulted in an overflow."

        case "modulo" | "%" | "mod":
            if num_b == 0:
                return "Error: Modulo by zero is not allowed."
            result = num_a % num_b

        case _:
            return (
                f"Error: Unknown operation '{operation}'. "
                "Supported operations: add (+), subtract (-), multiply (*), "
                "divide (/), power (^), modulo (%)."
            )

    # Return integer if there is no decimal component (e.g. 5.0 -> 5)
    if isinstance(result, float) and result.is_integer():
        return int(result)

    return result


# Tool definition compatible with OpenAI / Hugging Face Chat Completions API
CALCULATOR_TOOL = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": (
            "Perform basic arithmetic calculations such as addition (+), "
            "subtraction (-), multiplication (*), division (/), power (**), "
            "and modulo (%). Use this tool whenever you need to compute mathematical "
            "results accurately."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "The math operation to perform.",
                    "enum": ["add", "subtract", "multiply", "divide", "power", "modulo"],
                },
                "a": {
                    "type": "number",
                    "description": "The first number (left operand).",
                },
                "b": {
                    "type": "number",
                    "description": "The second number (right operand).",
                },
            },
            "required": ["operation", "a", "b"],
        },
    },
}


if __name__ == "__main__":
    print("=== Calculator Tool Test ===")
    test_cases = [
        ("add", 12, 8),
        ("subtract", 25, 7),
        ("multiply", 9, 6),
        ("divide", 144, 12),
        ("divide", 10, 0),
        ("power", 2, 8),
        ("modulo", 29, 5),
        ("modulo", 10, 0),
        ("unknown", 1, 1),
    ]

    for op, a, b in test_cases:
        res = calculate(op, a, b)
        print(f"calculate('{op}', {a}, {b}) => {res}")
