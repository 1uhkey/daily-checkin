"""
每日打卡 (DailyCheckin) —— 多 Agent 协作的家庭日常关怀系统

管道流程：
  Collector → Analyzer → Generator → Pusher

使用方式:
  python -m src.main "今天8点起床去健身房，中午和同事吃了川菜，下午写了3小时代码，晚上7点到家"

环境要求:
  在 .env 中设置 ANTHROPIC_API_KEY
"""

from __future__ import annotations

import time
import sys

from anthropic import Anthropic
from rich.console import Console
from rich.panel import Panel

from .agents import AnalyzerAgent, CollectorAgent, GeneratorAgent, PusherAgent
from .models.schemas import OrchestrationResult
from .storage import Journal
from .utils import load_config

console = Console()


def run_pipeline(user_input: str) -> OrchestrationResult:
    """执行完整的多 Agent 管道。"""
    result = OrchestrationResult()
    t0 = time.perf_counter()

    try:
        config = load_config()
    except RuntimeError as e:
        console.print(f"[red]配置错误: {e}[/red]")
        result.errors.append(str(e))
        return result

    client = Anthropic(api_key=config["api_key"])
    model = config["model"]

    # ── Agent 1: Collector ──────────────────────────────
    collector = CollectorAgent(client, model)
    raw_entries = collector.execute(user_input)
    result.raw_entries = raw_entries
    if not raw_entries:
        result.errors.append("未采集到任何记录")
        return result

    # ── Agent 2: Analyzer ───────────────────────────────
    analyzer = AnalyzerAgent(client, model)
    analyzed_entries = analyzer.execute(raw_entries)
    result.analyzed_entries = analyzed_entries

    # ── Agent 3: Generator ──────────────────────────────
    generator = GeneratorAgent(client, model)
    report = generator.execute(analyzed_entries)
    result.report = report

    # ── Agent 4: Pusher ─────────────────────────────────
    pusher = PusherAgent(client, model)
    status = pusher.execute(report)
    result.push_status = status

    # ── Persist ─────────────────────────────────────────
    journal = Journal()
    journal.save_result(result)

    result.elapsed_seconds = time.perf_counter() - t0
    return result


def main():
    if len(sys.argv) < 2:
        console.print(Panel.fit(
            "[bold cyan]每日打卡[/bold cyan] —— 多 Agent 家庭日常关怀系统\n\n"
            "用法: python -m src.main \"<你的每日记录>\"\n\n"
            "示例:\n"
            "  python -m src.main \"今天8点起床跑步，中午和同事吃了川菜，晚上看了电影\"",
            title="使用方法"
        ))
        return

    user_input = " ".join(sys.argv[1:])
    console.print(f"\n[bold]📝 原始输入:[/bold] {user_input[:100]}{'...' if len(user_input) > 100 else ''}\n")

    result = run_pipeline(user_input)

    if result.errors:
        console.print(f"\n[red]❌ 错误: {result.errors}[/red]")
    else:
        console.print(f"\n[bold green]✅ 完成！总耗时 {result.elapsed_seconds:.1f}s[/bold green]")
        console.print(f"   [dim]Agent 调用次数: 1 + {len(result.raw_entries)} + 1 + 1 = {len(result.raw_entries) + 3}[/dim]")


if __name__ == "__main__":
    main()
