"""
Workflow Engine (Section 5.3 'Workflow', Section 8.1 POST /v1/runs).

This is a deliberately simple, synchronous ReAct-style loop:
  1. Build the message list (optionally from a stored Prompt template).
  2. Call Groq, advertising any requested tools.
  3. If the model requests a tool call, execute it and feed the result back.
  4. Repeat until the model returns a final answer or a step limit is hit.

Each step is persisted as a TraceEvent for observability (Section 5, "M").
"""

from __future__ import annotations

import time
from typing import Any

from sqlalchemy.orm import Session

from app import models
from app.llm.groq_client import chat_completion
from app.tools.registry import execute_tool, list_tool_schemas

MAX_STEPS = 5


def _record_trace(db: Session, run_id: str, step: str, detail: dict[str, Any]) -> None:
    event = models.TraceEvent(run_id=run_id, step=step, detail=detail)
    db.add(event)
    db.commit()


def run_workflow(
    db: Session,
    run: models.Run,
    prompt_template: str | None,
    model: str | None,
    tool_names: list[str],
) -> dict[str, Any]:
    task = run.input_payload.get("task", "")
    system_prompt = prompt_template or (
        "You are an AI developer assistant. Complete the given task clearly and concisely. "
        "Use tools when they would materially improve the answer."
    )
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task},
    ]
    tool_schemas = list_tool_schemas(tool_names) if tool_names else None

    start = time.perf_counter()
    _record_trace(db, run.id, "workflow_start", {"task": task, "tools": tool_names})

    final_content = None
    total_usage: dict[str, Any] = {}

    for step_index in range(MAX_STEPS):
        result = chat_completion(messages=messages, model=model, tools=tool_schemas)
        _record_trace(
            db,
            run.id,
            f"model_call_{step_index}",
            {"content": result["content"], "tool_calls": result["tool_calls"], "usage": result["usage"]},
        )
        for key, value in (result["usage"] or {}).items():
            total_usage[key] = total_usage.get(key, 0) + value

        if result["tool_calls"]:
            messages.append({"role": "assistant", "content": result["content"] or "", "tool_calls": result["tool_calls"]})
            for call in result["tool_calls"]:
                fn_name = call["function"]["name"]
                try:
                    import json as _json

                    fn_args = _json.loads(call["function"]["arguments"] or "{}")
                    tool_result = execute_tool(fn_name, fn_args)
                    success = True
                except Exception as exc:  # noqa: BLE001
                    tool_result = {"error": str(exc)}
                    success = False

                _record_trace(db, run.id, f"tool_call_{fn_name}", {"arguments": call["function"]["arguments"], "result": tool_result, "success": success})
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "content": str(tool_result),
                    }
                )
            continue

        final_content = result["content"]
        break

    latency_ms = (time.perf_counter() - start) * 1000
    output_payload = {"result": final_content, "usage": total_usage}
    _record_trace(db, run.id, "workflow_complete", {"latency_ms": latency_ms})

    return {"output_payload": output_payload, "latency_ms": latency_ms}
