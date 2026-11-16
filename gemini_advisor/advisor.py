"""Advisor tool for Gemini and Google Antigravity agents.

A fast executor model calls the advisor tool to get guidance from a stronger
Gemini model, the same pattern as Claude's advisor tool.

The tool is a plain Python function, so it works in both places:

    # Google Antigravity SDK
    LocalAgentConfig(tools=[make_advisor_tool(max_uses=3)])

    # google-genai automatic function calling
    client.models.generate_content(
        model="gemini-flash-latest",
        contents=...,
        config={"tools": [make_advisor_tool()]},
    )

Unlike Claude's advisor, the advisor does not see the full transcript
automatically. The executor passes the question and any context it wants the
advisor to use.
"""

from __future__ import annotations

import threading
from typing import Any, Callable, Optional

DEFAULT_ADVISOR_MODEL = "gemini-3.1-pro-preview"
DEFAULT_MAX_USES = 5

_SYSTEM_PROMPT = (
    "You are a senior reviewer advising a faster executor model that is "
    "working on a task. Read the question and context, then give a focused "
    "plan, correction, or answer. Be concrete and brief: at most {max_words} "
    "words. Name the main risk and the single most important next step."
)


def make_advisor_tool(
    advisor_model: str = DEFAULT_ADVISOR_MODEL,
    *,
    api_key: Optional[str] = None,
    max_uses: Optional[int] = DEFAULT_MAX_USES,
    max_words: int = 120,
    thinking_level: Optional[str] = None,
    max_output_tokens: int = 1024,
    client: Any = None,
) -> Callable[..., str]:
    """Build an `advisor` function to hand to an agent as a tool.

    Args:
        advisor_model: Stronger Gemini model used as the reviewer.
        api_key: Gemini API key. Defaults to the GEMINI_API_KEY env var.
        max_uses: Maximum advisor calls for the tool instance. None means no cap.
        max_words: Soft length limit requested from the advisor.
        thinking_level: Optional thinking level for the advisor (e.g. "high").
        max_output_tokens: Cap on the advisor's output tokens per call.
        client: Optional preconstructed google-genai client (useful for tests).

    Returns:
        A function `advisor(question, context="") -> str` with a docstring
        and type hints, which agent frameworks read as the tool schema.
    """
    state = {"uses": 0}
    lock = threading.Lock()
    system_instruction = _SYSTEM_PROMPT.format(max_words=max_words)
    genai_client = client

    def _get_client() -> Any:
        nonlocal genai_client
        if genai_client is None:
            from google import genai  # imported lazily; only needed for real calls

            genai_client = genai.Client(api_key=api_key)
        return genai_client

    def advisor(question: str, context: str = "") -> str:
        """Ask a stronger reviewer model for guidance on a hard decision.

        Call this before committing to an approach, when you are stuck or
        errors keep recurring, or before declaring the task done. The reviewer
        sees only what you pass here, so include the goal, what you tried, and
        any relevant errors or file contents in `context`.

        Args:
            question: The specific decision or problem you need advice on.
            context: Relevant facts: the goal, what you tried, errors, snippets.

        Returns:
            The reviewer's advice as plain text.
        """
        with lock:
            if max_uses is not None and state["uses"] >= max_uses:
                return (
                    f"Advisor limit reached ({max_uses} calls). Continue on "
                    "your own judgment."
                )
            state["uses"] += 1

        prompt = f"Question:\n{question}\n\nContext:\n{context or '(none)'}"
        config: dict[str, Any] = {
            "system_instruction": system_instruction,
            "max_output_tokens": max_output_tokens,
        }
        if thinking_level is not None:
            config["thinking_config"] = {"thinking_level": thinking_level}

        try:
            response = _get_client().models.generate_content(
                model=advisor_model,
                contents=prompt,
                config=config,
            )
        except Exception as exc:  # the executor should keep working without advice
            return f"Advisor unavailable ({type(exc).__name__}). Continue on your own judgment."

        text = (getattr(response, "text", None) or "").strip()
        return text or "Advisor returned no advice. Continue on your own judgment."

    return advisor
