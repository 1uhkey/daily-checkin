from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from anthropic import Anthropic
from rich.console import Console

from ..models.schemas import EntryType, RawEntry
from .base import BaseAgent

console = Console()


class CollectorAgent(BaseAgent):
    """采集 Agent —— 负责接收并结构化用户当日碎片输入。

    输入：用户提供的文本 / 语音转录 / 照片描述
    输出：结构化的 RawEntry 列表

    这是多 Agent 管道的第一环。
    """

    @property
    def name(self) -> str:
        return "Collector"

    def _system_prompt(self) -> str:
        return (
            "你是一个细心的日记整理助手。用户将提供今天零散的日常记录（可能包含多条），"
            "请你将它们拆分为独立的事件条目，每条提取时间、类型、内容、地点和标签。\n\n"
            "严格按以下 JSON 数组格式输出，不要添加任何额外文字：\n"
            '[{"timestamp": "HH:MM", "type": "text/voice/photo", "content": "...", "location": "...", "tags": ["..."]}]\n\n'
            "规则：\n"
            "- 时间用 HH:MM 格式（24小时制），如果用户没提时间就填 00:00\n"
            "- type 默认 text\n"
            "- location 可以为 null\n"
            "- tags 提取 2-4 个关键词\n"
            "- 每一条原始信息对应一个条目"
        )

    def execute(self, user_input: str, **kwargs: Any) -> list[RawEntry]:
        console.print(f"[bold cyan]═══ Agent: {self.name} 开始采集 ═══[/bold cyan]")
        response = self._call(user_input)
        try:
            items = json.loads(response)
        except json.JSONDecodeError:
            # fallback: treat whole input as one entry
            items = [{"timestamp": "00:00", "type": "text", "content": user_input, "location": None, "tags": []}]

        today = datetime.now().strftime("%Y-%m-%d")
        entries = []
        for item in items:
            try:
                ts = datetime.strptime(f"{today} {item['timestamp']}", "%Y-%m-%d %H:%M")
            except ValueError:
                ts = datetime.now()
            entry = RawEntry(
                timestamp=ts,
                type=EntryType(item.get("type", "text")),
                content=item.get("content", ""),
                location=item.get("location"),
                tags=item.get("tags", []),
            )
            entries.append(entry)

        console.print(f"  [green]✓ 采集到 {len(entries)} 条记录[/green]")
        return entries
