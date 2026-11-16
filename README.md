# gemini-advisor: advisor tool for Gemini and Google Antigravity agents

**gemini-advisor** gives a Gemini or Google Antigravity agent an `advisor` tool.
A fast executor model (such as `gemini-flash-latest`) calls it to get focused
guidance from a stronger Gemini model (such as `gemini-3.1-pro-preview`) before
committing to an approach, when stuck, or before declaring a task done. It is
modeled on Claude's advisor tool.

- Works as a tool in the **Google Antigravity SDK** (`LocalAgentConfig(tools=[...])`)
- Works with **google-genai** automatic function calling
- Per-agent call cap, errors returned as text (the run keeps going), optional thinking level
- Python, MIT license

Agent skill: [`skills/gemini-advisor/SKILL.md`](skills/gemini-advisor/SKILL.md) · Machine-readable summary: [`llms.txt`](llms.txt)

## Install

```bash
pip install google-genai
git clone https://github.com/NiksheyYadav/gemini-advisor
cd gemini-advisor
```

Set `GEMINI_API_KEY` in your environment.

## Usage

Google Antigravity SDK (`pip install google-antigravity`):

```python
from google.antigravity import Agent, LocalAgentConfig
from gemini_advisor import make_advisor_tool

config = LocalAgentConfig(
    tools=[make_advisor_tool(max_uses=3, thinking_level="high")],
)
async with Agent(config) as agent:
    response = await agent.chat("...")
    print(await response.text())
```

google-genai automatic function calling:

```python
from google import genai
from gemini_advisor import make_advisor_tool

client = genai.Client()
resp = client.models.generate_content(
    model="gemini-flash-latest",
    contents="...",
    config={"tools": [make_advisor_tool()]},
)
```

## Options

| Option | Default | Meaning |
| --- | --- | --- |
| `advisor_model` | `gemini-3.1-pro-preview` | Stronger reviewer model |
| `max_uses` | `5` | Advisor calls per tool instance; `None` for no cap |
| `max_words` | `120` | Soft length limit requested from the advisor |
| `thinking_level` | `None` | Passed as `thinking_config.thinking_level` |
| `max_output_tokens` | `1024` | Output cap per call |
| `api_key` | `GEMINI_API_KEY` | Explicit key, if not set in the environment |

## How it differs from Claude's advisor

- **No automatic transcript.** Claude's advisor reads the whole conversation on
  the server. A Python tool only sees its arguments, so the executor passes a
  `question` and `context`.
- **Client-side.** Each advisor call is a normal Gemini request, billed as one.
- **Failures don't stop the run.** API errors and an exhausted cap return a text
  message so the executor can continue.

Google's Agent Development Kit (ADK) has a similar built-in tool, `ModelConsultTool`,
for ADK agents. This package targets the Antigravity SDK and plain google-genai.

## Status

Unit-tested with a fake Gemini client; no network calls in the tests. **Not yet
verified against the live Gemini API or the Antigravity runtime.** Run one live
call before relying on it.

## Tests

```bash
python -m unittest discover -s tests -v
```

## License

MIT. See [LICENSE](LICENSE).
