import os
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gemini_advisor.advisor import make_advisor_tool  # noqa: E402


class FakeModels:
    def __init__(self, reply="Do X first.", error=None):
        self.reply = reply
        self.error = error
        self.calls = []

    def generate_content(self, model, contents, config):
        self.calls.append({"model": model, "contents": contents, "config": config})
        if self.error:
            raise self.error
        return SimpleNamespace(text=self.reply)


class FakeClient:
    def __init__(self, **kwargs):
        self.models = FakeModels(**kwargs)


class AdvisorToolTests(unittest.TestCase):
    def test_returns_advice_and_sends_question_and_context(self):
        client = FakeClient(reply="  Use a WaitGroup.  ")
        advisor = make_advisor_tool(client=client, advisor_model="gemini-test-pro")
        out = advisor("How to shut down?", "Goroutine pool, 10 workers")
        self.assertEqual(out, "Use a WaitGroup.")
        call = client.models.calls[0]
        self.assertEqual(call["model"], "gemini-test-pro")
        self.assertIn("How to shut down?", call["contents"])
        self.assertIn("Goroutine pool, 10 workers", call["contents"])
        self.assertIn("system_instruction", call["config"])
        self.assertEqual(call["config"]["max_output_tokens"], 1024)

    def test_thinking_level_is_passed_only_when_set(self):
        client = FakeClient()
        make_advisor_tool(client=client, thinking_level="high")("q")
        self.assertEqual(
            client.models.calls[0]["config"]["thinking_config"],
            {"thinking_level": "high"},
        )
        client2 = FakeClient()
        make_advisor_tool(client=client2)("q")
        self.assertNotIn("thinking_config", client2.models.calls[0]["config"])

    def test_max_uses_cap_is_enforced(self):
        client = FakeClient()
        advisor = make_advisor_tool(client=client, max_uses=2)
        advisor("a")
        advisor("b")
        out = advisor("c")
        self.assertIn("limit reached", out)
        self.assertEqual(len(client.models.calls), 2)

    def test_no_cap_when_max_uses_is_none(self):
        client = FakeClient()
        advisor = make_advisor_tool(client=client, max_uses=None)
        for _ in range(7):
            advisor("q")
        self.assertEqual(len(client.models.calls), 7)

    def test_api_error_does_not_raise(self):
        client = FakeClient(error=RuntimeError("boom"))
        advisor = make_advisor_tool(client=client)
        out = advisor("q")
        self.assertIn("unavailable", out)
        self.assertIn("RuntimeError", out)

    def test_empty_reply_gets_fallback_text(self):
        client = FakeClient(reply="   ")
        out = make_advisor_tool(client=client)("q")
        self.assertIn("no advice", out)

    def test_function_has_docstring_and_signature_for_tool_schema(self):
        advisor = make_advisor_tool(client=FakeClient())
        self.assertEqual(advisor.__name__, "advisor")
        self.assertIn("reviewer", advisor.__doc__)
        self.assertEqual(list(advisor.__code__.co_varnames[:2]), ["question", "context"])


if __name__ == "__main__":
    unittest.main()
