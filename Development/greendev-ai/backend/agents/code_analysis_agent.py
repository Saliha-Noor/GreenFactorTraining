"""
Agent 1 — Code Analysis Agent
Parses Python code using the ast module.
Does NOT execute the code.
"""

import ast
import re


def analyze_code(code_string: str) -> dict:
    try:
        tree = ast.parse(code_string)
    except SyntaxError as e:
        return {"error": f"Syntax error in code: {e}"}

    functions    = 0
    loops        = 0
    nested_loops = 0
    classes      = 0
    imports      = 0
    comprehensions = 0
    recursion_calls = set()
    function_names  = set()

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions += 1
            function_names.add(node.name)
        elif isinstance(node, ast.ClassDef):
            classes += 1
        elif isinstance(node, (ast.For, ast.While)):
            loops += 1
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            imports += 1
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            comprehensions += 1

    # Detect nested loops (rough measure)
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)):
            for child in ast.walk(node):
                if child is not node and isinstance(child, (ast.For, ast.While)):
                    nested_loops += 1
                    break

    # Detect recursion
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in function_names:
                recursion_calls.add(node.func.id)

    lines        = [l for l in code_string.splitlines() if l.strip()]
    total_lines  = len(lines)
    comment_lines = len([l for l in code_string.splitlines() if l.strip().startswith('#')])

    # Complexity score (rough cyclomatic)
    complexity = 1 + loops + nested_loops + len([
        n for n in ast.walk(tree)
        if isinstance(n, (ast.If, ast.ExceptHandler, ast.With, ast.Assert))
    ])

    # Detect task type for benchmark matching
    task_type = _detect_task_type(code_string, tree)

    return {
        "functions":       functions,
        "loops":           loops,
        "nested_loops":    nested_loops,
        "classes":         classes,
        "imports":         imports,
        "comprehensions":  comprehensions,
        "recursion":       len(recursion_calls) > 0,
        "lines":           total_lines,
        "comment_lines":   comment_lines,
        "complexity":      complexity,
        "task_type":       task_type,
    }


def _detect_task_type(code_string: str, tree: ast.AST) -> str:
    """
    Heuristically detect task type for benchmark dataset matching.
    """
    code_lower = code_string.lower()

    if any(kw in code_lower for kw in ["sort", "sorted", "bubble", "merge", "quick", "heap"]):
        return "sorting"
    if any(kw in code_lower for kw in ["fibonacci", "fib", "factorial", "recursi"]):
        return "fibonacci"
    if any(kw in code_lower for kw in ["matrix", "numpy", "dot(", "matmul"]):
        return "matrix-multiply"
    if any(kw in code_lower for kw in ["tree", "node", "bst", "binary tree"]):
        return "binary-trees"
    if any(kw in code_lower for kw in ["regex", "re.match", "re.findall", "re.sub", "pattern"]):
        return "regex"
    if any(kw in code_lower for kw in ["open(", "read(", "write(", "file", "csv", "json.load"]):
        return "io-heavy"
    if any(kw in code_lower for kw in ["str", "split", "join", "replace", "upper", "lower"]):
        return "string-processing"

    return "general"
