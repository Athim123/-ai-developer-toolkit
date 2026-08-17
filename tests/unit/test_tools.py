from app.tools.registry import execute_tool


def test_calculator_basic():
    result = execute_tool("calculator", {"expression": "2 + 2 * 3"})
    assert result["result"] == 8


def test_calculator_rejects_unsafe():
    import pytest

    with pytest.raises(ValueError):
        execute_tool("calculator", {"expression": "__import__('os').system('echo hi')"})


def test_word_count():
    result = execute_tool("word_count", {"text": "hello world"})
    assert result["words"] == 2
    assert result["characters"] == 11


def test_echo():
    result = execute_tool("echo", {"a": 1})
    assert result == {"echo": {"a": 1}}
