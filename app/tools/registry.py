"""
Tool Execution Service (Section 5.3 'Tooling').

Tools are plain Python callables registered here with a JSON-schema style
description, so they can be (a) invoked directly via POST /v1/tools/execute
and (b) advertised to the LLM as callable functions during a workflow run.
"""

from __future__ import annotations

import ast
import operator as op
from typing import Any, Callable

_SAFE_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.Mod: op.mod,
}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPERATORS:
        return _SAFE_OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPERATORS:
        return _SAFE_OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsupported or unsafe expression")


def tool_calculator(arguments: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a basic arithmetic expression safely (no eval())."""
    expression = arguments.get("expression", "")
    try:
        tree = ast.parse(expression, mode="eval").body
        result = _safe_eval(tree)
        return {"expression": expression, "result": result}
    except Exception as exc:
        raise ValueError(f"Could not evaluate expression: {exc}") from exc


def tool_echo(arguments: dict[str, Any]) -> dict[str, Any]:
    """Debug tool: echoes back whatever arguments it received."""
    return {"echo": arguments}


def tool_word_count(arguments: dict[str, Any]) -> dict[str, Any]:
    """Counts words/characters in a piece of text."""
    text = arguments.get("text", "")
    return {"words": len(text.split()), "characters": len(text)}


# name -> (callable, json_schema)
TOOL_REGISTRY: dict[str, tuple[Callable[[dict], dict], dict]] = {
    "calculator": (
        tool_calculator,
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Evaluate a basic arithmetic expression.",
                "parameters": {
                    "type": "object",
                    "properties": {"expression": {"type": "string"}},
                    "required": ["expression"],
                },
            },
        },
    ),
    "echo": (
        tool_echo,
        {
            "type": "function",
            "function": {
                "name": "echo",
                "description": "Echo back the given arguments (debug tool).",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    ),
    "word_count": (
        tool_word_count,
        {
            "type": "function",
            "function": {
                "name": "word_count",
                "description": "Count words and characters in text.",
                "parameters": {
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                },
            },
        },
    ),
}


def list_tool_schemas(names: list[str] | None = None) -> list[dict]:
    if names is None:
        return [schema for _, schema in TOOL_REGISTRY.values()]
    return [TOOL_REGISTRY[name][1] for name in names if name in TOOL_REGISTRY]


def execute_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name not in TOOL_REGISTRY:
        raise KeyError(f"Unknown tool: {name}")
    func, _ = TOOL_REGISTRY[name]
    return func(arguments)
