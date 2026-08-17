"""
Evaluation Service (Section 4.1 #4 / 5.3 'Eval').

Uses the same Groq model as an LLM-as-judge to score a completed run's
output against a set of criteria, returning a structured JSON scorecard.
"""

from __future__ import annotations

import json

from app import models
from app.llm.groq_client import chat_completion

JUDGE_SYSTEM_PROMPT = (
    "You are a strict evaluation judge for an AI developer workflow run. "
    "Score the OUTPUT against the given INPUT on each requested criterion, "
    "from 0.0 (fails) to 1.0 (excellent). "
    "Respond ONLY with JSON: "
    '{"scores": {"<criterion>": <float>, ...}, "rationale": "<short text>"}'
)


def evaluate_run(run: models.Run, criteria: list[str]) -> dict:
    user_prompt = (
        f"INPUT:\n{json.dumps(run.input_payload)}\n\n"
        f"OUTPUT:\n{json.dumps(run.output_payload)}\n\n"
        f"CRITERIA: {', '.join(criteria)}"
    )
    result = chat_completion(
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=400,
    )
    raw = result["content"] or "{}"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        # Fall back to a neutral score if the judge didn't return valid JSON
        parsed = {"scores": {c: 0.5 for c in criteria}, "rationale": "Judge response was not valid JSON."}

    scores = {c: float(parsed.get("scores", {}).get(c, 0.0)) for c in criteria}
    rationale = parsed.get("rationale", "")
    return {"scores": scores, "rationale": rationale}
