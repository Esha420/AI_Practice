#tools/calculator.py
from sympy import sympify

def calculator(expression):
    """
    Safely evaluate a mathematical expression.
    """
    try:
        result = sympify(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"
