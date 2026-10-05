"""OpenAI-compatible client for the subject model + summary compactor."""

import json
import os
import urllib.request


class ChatClient:
    def __init__(self, base_url, api_key=None, model=None, timeout=600):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.environ.get("GOLDFISH_API_KEY", "")
        self.model = model
        self.timeout = timeout

    def chat(self, messages, max_tokens=700, temperature=0.0):
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        req = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json",
                     "Authorization": "***" + self.api_key},
            method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            body = json.loads(resp.read().decode())
        msg = body["choices"][0]["message"]
        content = msg.get("content")
        if content is None:
            # reasoning-thinking servers return content=None when the token
            # budget is consumed by reasoning; fall back to the reasoning text
            # so the scorer still sees any GOLD token the model recalled.
            content = msg.get("reasoning") or msg.get("reasoning_content") or "YOU_FORGOT"
        return content

    def count_tokens_approx(self, messages):
        """Cheap char/4 estimate; vLLM ignores extra fields so exact count via
        a generate call is wasteful. Estimates are labeled in reports."""
        return sum(len(m.get("content", "")) for m in messages) // 4 + 4 * len(messages)
