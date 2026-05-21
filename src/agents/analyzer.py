from __future__ import annotations

import json
from typing import Any

from anthropic import Anthropic
from rich.console import Console

from ..models.schemas import AnalyzedEntry, RawEntry
from .base import BaseAgent

console = Console()


class AnalyzerAgent(BaseAgent):
    """理解与分析 Agent —— 管道第二环。

    对每个 RawEntry 进行语义理解：
    - 事件摘要
    - 情绪识别
    - 关键词提取
    - 是否值得高亮（highlight）
    - 从父母视角的解读

    这是长链推理的核心环节：需要先在上下文中理解事件，
    再换位到父母视角（通常是 50-60 岁长辈）进行二次解读。
    """

    @property
    def name(self) -> str:
        return "Analyzer"

    def _system_prompt(self) -> str:
        return (
            "你是一个情感细腻的生活观察者，擅长从日常琐事中发现温暖和意义。"
            "用户会提供今天的一条事件记录，请你做两件事：\n\n"
            "1. **自我理解**：这条记录说了什么？当事人在经历什么情绪？\n"
            "2. **父母视角解读**：如果是你 50-60 岁的父母看到这条记录，他们最关心的是什么？"
            "（比如：有没有好好吃饭、工作累不累、心情好不好、有没有什么有趣的事）\n\n"
            "严格按以下 JSON 格式输出，不要添加额外文字：\n"
            '{"summary": "...", "mood": "happy/calm/tired/stressed/excited/neutral", '
            '"keywords": ["..."], "highlight": true/false, "parent_perspective": "..."}\n\n'
            "规则：\n"
            "- summary 一句话概括（15字内）\n"
            "- mood 从 happy/calm/tired/stressed/excited/neutral 中选一个\n"
            "- keywords 2-3个关键词\n"
            "- highlight: 如果有成就感、美食、社交、运动等值得分享的事则为 true\n"
            "- parent_perspective: 模仿父母关心的角度写一句话（如'今天加班到这么晚，孩子辛苦了'）"
        )

    def execute(self, entries: list[RawEntry], **kwargs: Any) -> list[AnalyzedEntry]:
        console.print(f"[bold cyan]═══ Agent: {self.name} 开始分析 ═══[/bold cyan]")
        analyzed: list[AnalyzedEntry] = []

        for entry in entries:
            prompt = (
                f"事件：{entry.content}\n"
                f"时间：{entry.timestamp.strftime('%H:%M')}\n"
                f"标签：{', '.join(entry.tags) if entry.tags else '无'}"
            )
            response = self._call(prompt)
            try:
                data = json.loads(response)
            except json.JSONDecodeError:
                data = {
                    "summary": entry.content[:20],
                    "mood": "neutral",
                    "keywords": entry.tags,
                    "highlight": False,
                    "parent_perspective": "今天过得怎么样呀？",
                }

            ae = AnalyzedEntry(
                raw=entry,
                summary=data.get("summary", entry.content[:20]),
                mood=data.get("mood", "neutral"),
                keywords=data.get("keywords", entry.tags),
                highlight=data.get("highlight", False),
                parent_perspective=data.get("parent_perspective", ""),
            )
            analyzed.append(ae)

        highlights = sum(1 for a in analyzed if a.highlight)
        console.print(f"  [green]✓ 分析了 {len(analyzed)} 条，其中 {highlights} 条亮点[/green]")
        return analyzed
