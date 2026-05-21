from __future__ import annotations

from typing import Any

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anthropic import Anthropic

from rich.console import Console

from ..models.schemas import AnalyzedEntry, DailyReport
from .base import BaseAgent

console = Console()


class GeneratorAgent(BaseAgent):
    """日报生成 Agent —— 管道第三环。

    将分析后的当日事件聚合为一份"给父母看的温馨日报"。

    这是多 Agent 协作中"从数据到可消费内容"的关键转换环节——
    不是冷冰冰的数据罗列，而是有温度的、长辈能看懂且感到被关怀的文字。
    """

    @property
    def name(self) -> str:
        return "Generator"

    def _system_prompt(self) -> str:
        return (
            "你是一个温暖的家庭日报编辑。你的任务是把一个年轻人今天的日常记录，"
            "编辑成一份给 TA 父母看的温馨日报。\n\n"
            "读者画像：50-60 岁的中国父母，关心孩子的健康、工作、心情和社交生活。\n"
            "风格要求：\n"
            "- 口语化、亲切、有温度，像家书一样\n"
            "- 不要过于正式，可以用一些可爱的语气\n"
            "- 把重点放在'孩子今天过得好不好'这件事上\n"
            "- 如果今天有亮点事件（美食、成就、社交），重点描写\n"
            "- 结尾给一个温暖的收尾\n\n"
            "请严格按以下结构输出（用标记分隔）：\n\n"
            "---TITLE---\n"
            "一个温馨的日报标题（如：🌅 小明的今日时光 · 3月15日）\n\n"
            "---GREETING---\n"
            "开头问候语，1-2句话\n\n"
            "---HIGHLIGHTS---\n"
            "今日亮点，每条一行，用 - 开头\n\n"
            "---TIMELINE---\n"
            "按时间线梳理今天，每条一行，用 - 开头\n\n"
            "---MOOD---\n"
            "今天整体的情绪总结，1-2句话\n\n"
            "---CLOSING---\n"
            "温馨结尾，1-2句话"
        )

    def execute(self, analyzed_entries: list[AnalyzedEntry], **kwargs: Any) -> DailyReport:
        console.print(f"[bold cyan]═══ Agent: {self.name} 开始生成日报 ═══[/bold cyan]")

        # Build a compact input for the LLM
        lines: list[str] = []
        for entry in analyzed_entries:
            time_str = entry.raw.timestamp.strftime("%H:%M")
            mood_emoji = {
                "happy": "😊", "calm": "😌", "tired": "😴",
                "stressed": "😰", "excited": "🎉", "neutral": "💭",
            }.get(entry.mood.value if hasattr(entry.mood, 'value') else entry.mood, "💭")
            lines.append(
                f"[{time_str}] {mood_emoji} {entry.summary} "
                f"| 父母视角: {entry.parent_perspective}"
            )

        prompt = "以下是今天所有事件的汇总：\n\n" + "\n".join(lines)
        response = self._call(prompt, max_tokens=1024)

        # Parse structured output
        def _extract(tag: str, text: str) -> str:
            start_marker = f"---{tag}---"
            end_markers = [m for m in [
                "---TITLE---", "---GREETING---", "---HIGHLIGHTS---",
                "---TIMELINE---", "---MOOD---", "---CLOSING---"
            ] if m != start_marker]
            start = text.find(start_marker)
            if start == -1:
                return ""
            start += len(start_marker)
            end = min(
                (text.find(m, start) for m in end_markers if text.find(m, start) != -1),
                default=len(text)
            )
            return text[start:end].strip()

        report = DailyReport(
            title=_extract("TITLE", response),
            greeting=_extract("GREETING", response),
            highlights=[h.strip("- ") for h in _extract("HIGHLIGHTS", response).split("\n") if h.strip()],
            timeline=[t.strip("- ") for t in _extract("TIMELINE", response).split("\n") if t.strip()],
            mood_summary=_extract("MOOD", response),
            closing=_extract("CLOSING", response),
            raw_entries_count=len(analyzed_entries),
        )

        console.print(f"  [green]✓ 日报生成完成: {report.title}[/green]")
        return report
