# tools/code_tool.py
import sys
import io
import traceback

def code_tool(code_snippet):
    """
    Execute a small Python code snippet safely and return the result.
    Captures stdout, stderr, and errors.
    """
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()

    try:
        # Only allow simple Python code
        exec(code_snippet, {"__builtins__": {"print": print, "sum": sum, "len": len, "max": max, "min": min, "range": range}})
        output = redirected_output.getvalue()
        error = redirected_error.getvalue()
        if error:
            return f"Error: {error.strip()}"
        return output.strip() if output.strip() else "Code executed successfully, no output."
    except Exception:
        return f"Exception:\n{traceback.format_exc()}"
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
