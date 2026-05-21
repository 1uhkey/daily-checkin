from __future__ import annotations

import abc
import time
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from anthropic import Anthropic


class BaseAgent(abc.ABC):
    """基础 Agent —— 所有专用 Agent 的父类。

    每个 Agent 封装一段可复用的 LLM 推理逻辑，接收输入 → 调用 Claude → 输出结构化结果。
    多 Agent 之间通过管道串联：Collector → Analyzer → Generator → Pusher。
    """

    def __init__(self, client: "Anthropic", model: str = "claude-sonnet-4-6"):
        self.client = client
        self.model = model

    @property
    @abc.abstractmethod
    def name(self) -> str: ...

    @abc.abstractmethod
    def _system_prompt(self) -> str: ...

    def _call(self, user_message: str, max_tokens: int = 2048) -> str:
        start = time.perf_counter()
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self._system_prompt(),
            messages=[{"role": "user", "content": user_message}],
        )
        elapsed = time.perf_counter() - start
        content = resp.content[0].text
        print(f"  [{self.name}] {elapsed:.2f}s | tokens in={resp.usage.input_tokens} out={resp.usage.output_tokens}")
        return content

    @abc.abstractmethod
    def execute(self, **kwargs: Any) -> Any: ...
