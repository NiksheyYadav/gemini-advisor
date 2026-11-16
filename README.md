# gemini-advisor

An advisor tool for Gemini and Google Antigravity agents, modeled on Claude's
advisor tool: a fast executor model consults a stronger reviewer model for
guidance mid-task.

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

google-genai automatic function calling (`pip install google-genai`):

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

## Differences from Claude's advisor

- **No automatic transcript.** Claude's advisor reads the full conversation on
  the server. A Python tool only sees its arguments, so the executor passes a
  `question` and `context`.
- **Client-side.** The advisor call is an ordinary `generate_content` call, not
  a server-side sub-inference. Costs are billed as normal Gemini calls.
- **Failures don't stop the run.** API errors return a text message so the
  executor keeps working.

## Options

| Option | Default | Meaning |
| --- | --- | --- |
| `advisor_model` | `gemini-3.1-pro-preview` | Stronger reviewer model |
| `max_uses` | `5` | Advisor calls per tool instance; `None` for no cap |
| `max_words` | `120` | Soft length limit requested from the advisor |
| `thinking_level` | `None` | Passed as `thinking_config.thinking_level` |
| `max_output_tokens` | `1024` | Cap on advisor output per call |

Google ADK already ships a similar tool, `ModelConsultTool`, for ADK agents.
This package targets the Antigravity SDK and plain google-genai.

## Tests

```bash
python -m unittest discover -s tests -v
```

The tests use a fake client, so they don't call the Gemini API. The tool has
not been run against the live API or the Antigravity runtime.
