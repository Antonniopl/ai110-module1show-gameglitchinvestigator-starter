"""Reproduce original helper bugs without importing or mocking Streamlit."""

import ast
import hashlib
from pathlib import Path


def main() -> None:
    """Execute only the exact starter helper definitions, not its UI code."""
    source_path = Path(__file__).resolve().parents[1] / "evidence/original_app.py.txt"
    source = source_path.read_bytes()
    digest = hashlib.sha1(
        b"blob " + str(len(source)).encode() + b"\0" + source
    ).hexdigest()
    expected = "6e097e34bbf88dbb6985e45705ac11c5983234ca"
    if digest != expected:
        raise RuntimeError("The saved starter source does not match its Git blob.")
    tree = ast.parse(source.decode("utf-8"))
    helpers = ast.Module(
        body=[node for node in tree.body if isinstance(node, ast.FunctionDef)],
        type_ignores=[],
    )
    namespace = {}
    exec(compile(helpers, str(source_path), "exec"), namespace)
    print("Original starter helper reproduction (not a browser play session)")
    print(f"Verified app.py Git blob: {digest}")
    cases = [
        ("check_guess", (60, 50)),
        ("check_guess", (40, 50)),
        ("check_guess", (9, "50")),
        ("parse_guess", ("40.9",)),
        ("parse_guess", ("-1",)),
        ("update_score", (0, "Too High", 2)),
    ]
    for function, args in cases:
        result = namespace[function](*args)
        print(f"{function}{args!r} -> {result!r}")
    print("All six calls completed; no runtime exception was raised.")


if __name__ == "__main__":
    main()
