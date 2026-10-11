"""LLM 客户端 + 从模型输出里抠 JSON 的工具。"""
import json

import requests


def extract_json(text: str):
    """从 LLM 输出里抠出第一个 JSON 数组/对象（容忍 ```json 围栏和前后废话）。"""
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        first_nl = text.find("\n")
        text = text[first_nl + 1:] if first_nl != -1 else text
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]
    for i, ch in enumerate(text):
        if ch in "[{":
            for end in range(len(text), i, -1):
                candidate = text[i:end]
                try:
                    return json.loads(candidate)
                except (json.JSONDecodeError, ValueError):
                    continue
            break
    return None


class LLM:
    def chat(self, messages: list[dict], temperature: float = 0.0) -> str:
        raise NotImplementedError


class DeepSeekLLM(LLM):
    """真实实现：requests 直连 DeepSeek（OpenAI 兼容接口）。"""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def chat(self, messages, temperature=0.0):
        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={"model": self.model, "messages": messages, "temperature": temperature},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


class FakeLLM(LLM):
    """测试用：按调用顺序返回预设响应。"""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def chat(self, messages, temperature=0.0):
        self.calls.append(messages)
        return self.responses.pop(0) if self.responses else "[]"
