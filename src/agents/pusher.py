from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anthropic import Anthropic

from rich.console import Console

from ..models.schemas import DailyReport
from .base import BaseAgent

console = Console()


class PusherAgent(BaseAgent):
    """推送 Agent —— 管道最后一环。

    负责将日报发送到外部渠道。当前支持：
    - 本地文件输出（默认，始终可用）
    - Webhook 推送（可配置）
    - 控制台打印（方便调试）
    """

    @property
    def name(self) -> str:
        return "Pusher"

    def _system_prompt(self) -> str:
        return ""

    def execute(self, report: DailyReport, **kwargs: Any) -> str:
        console.print(f"[bold cyan]═══ Agent: {self.name} 开始推送 ═══[/bold cyan]")

        # 1. Format the report
        report_text = self._format_report(report)

        # 2. Save to local file
        os.makedirs("data/reports", exist_ok=True)
        filename = f"data/reports/daily-{report.date}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_text)
        console.print(f"  [green]✓ 日报已保存: {filename}[/green]")

        # 3. Console preview
        console.print(f"\n[bold yellow]━━━ 日报预览 ━━━[/bold yellow]")
        console.print(report_text)

        # 4. Webhook (if configured)
        webhook_url = os.getenv("PUSH_WEBHOOK_URL")
        if webhook_url:
            import urllib.request

            payload = json.dumps({
                "type": "daily_checkin",
                "date": report.date,
                "title": report.title,
                "content": report_text,
                "generated_at": report.generated_at.isoformat(),
            }).encode()
            try:
                req = urllib.request.Request(webhook_url, data=payload, headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req)
                console.print("  [green]✓ Webhook 推送成功[/green]")
            except Exception as e:
                console.print(f"  [yellow]⚠ Webhook 推送失败: {e}[/yellow]")

        return "ok"

    def _format_report(self, report: DailyReport) -> str:
        highlights_block = "\n".join(f"✨ {h}" for h in report.highlights)
        timeline_block = "\n".join(f"🕐 {t}" for t in report.timeline)

        return f"""\
# {report.title}

{report.greeting}

---

## 今日亮点

{highlights_block}

## 时间线

{timeline_block}

## 心情小结

{report.mood_summary}

---

{report.closing}

> 🤖 由每日打卡多 Agent 系统自动生成 | {datetime.now().strftime('%Y-%m-%d %H:%M')}
> 共处理 {report.raw_entries_count} 条日常记录
"""
