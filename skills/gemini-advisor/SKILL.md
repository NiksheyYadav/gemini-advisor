---
name: gemini-advisor
description: Give a Gemini or Google Antigravity agent an advisor tool that consults a stronger Gemini model for planning, course correction, and review. Use when building an agent that should call a bigger reviewer model mid-task (the advisor pattern, like Claude's advisor tool), when wiring a Gemini Flash executor to a Gemini Pro advisor, or when adding a capped advisor tool to a Google Antigravity SDK agent or a google-genai function-calling loop.
---

# gemini-advisor

Adds an `advisor(question, context)` tool. A fast executor model calls it to get
focused guidance from a stronger Gemini model before committing to an approach,
when stuck, or before declaring a task done.

## When to use

- The executor is a cheaper Gemini model (for example `gemini-flash-latest`) and
  the hard decisions need a stronger one (for example `gemini-3.1-pro-preview`).
- You use the Google Antigravity SDK (`LocalAgentConfig(tools=[...])`) or the
  google-genai SDK with automatic function calling.

## Setup

```bash
pip install google-genai
# repo: https://github.com/NiksheyYadav/gemini-advisor
```

Set `GEMINI_API_KEY`, then:

```python
from gemini_advisor import make_advisor_tool

advisor = make_advisor_tool(max_uses=3, thinking_level="high")
```

Antigravity SDK:

```python
from google.antigravity import Agent, LocalAgentConfig

config = LocalAgentConfig(tools=[advisor])
async with Agent(config) as agent:
    print(await (await agent.chat("...")).text())
```

google-genai:

```python
from google import genai

client = genai.Client()
client.models.generate_content(
    model="gemini-flash-latest",
    contents="...",
    config={"tools": [advisor]},
)
```

## Options

| Option | Default | Purpose |
| --- | --- | --- |
| `advisor_model` | `gemini-3.1-pro-preview` | Stronger reviewer model |
| `max_uses` | `5` | Calls allowed per tool instance; `None` removes the cap |
| `max_words` | `120` | Soft length limit on advice |
| `thinking_level` | `None` | Thinking level for the advisor (e.g. `"high"`) |
| `max_output_tokens` | `1024` | Output cap per call |
| `api_key` | env `GEMINI_API_KEY` | Explicit key |

## Behaviour to know

- The advisor sees only the `question` and `context` the executor passes. Claude's
  advisor reads the whole transcript automatically; this one does not.
- API errors and an exhausted cap return text, not exceptions, so the run keeps going.
- Each call is a normal Gemini request and is billed as one.

## Status

Unit-tested with a fake client. Not yet verified against the live Gemini API or
the Antigravity runtime. Run one live call before relying on it in production.
