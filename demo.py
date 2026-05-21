"""
演示脚本 —— 不调用 API，用模拟数据展示完整管道流程。

运行: python demo.py
"""

from __future__ import annotations

import sys
import time
from datetime import datetime

# Windows 控制台强制 UTF-8，避免 emoji 乱码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.models.schemas import (
    AnalyzedEntry,
    DailyReport,
    EntryType,
    Mood,
    OrchestrationResult,
    RawEntry,
)


def simulate_pipeline(user_input: str) -> OrchestrationResult:
    """模拟完整的多 Agent 管道，无需 API Key。"""
    result = OrchestrationResult()
    t0 = time.perf_counter()

    print("═══ Agent: Collector 开始采集 ═══")
    # 模拟采集：按中英文逗号/句号拆分为独立事件
    today = datetime.now().strftime("%Y-%m-%d")
    text = user_input.replace("，", "|").replace("。", "|").replace(",", "|").replace(".", "|")
    parts = [p.strip() for p in text.split("|") if p.strip()]
    if not parts:
        parts = [user_input]

    for i, part in enumerate(parts):
        ts = datetime.strptime(f"{today} {8 + i:02d}:00", "%Y-%m-%d %H:%M")
        entry = RawEntry(
            timestamp=ts,
            type=EntryType.TEXT,
            content=part,
            tags=["日常"],
        )
        result.raw_entries.append(entry)

    print(f"  ✓ 采集到 {len(result.raw_entries)} 条记录")

    # 模拟分析
    print("═══ Agent: Analyzer 开始分析 ═══")
    mood_map = {"跑步": Mood.EXCITED, "健身": Mood.EXCITED, "加班": Mood.TIRED,
                "美食": Mood.HAPPY, "电影": Mood.HAPPY, "川菜": Mood.HAPPY,
                "代码": Mood.CALM, "开会": Mood.STRESSED}

    for entry in result.raw_entries:
        detected_mood = Mood.NEUTRAL
        for keyword, mood in mood_map.items():
            if keyword in entry.content:
                detected_mood = mood
                break

        parent_msgs = {
            "运动": "运动了好习惯，注意别太累哦",
            "跑步": "晨跑对身体好，记得拉伸",
            "健身": "锻炼是好事，要量力而行",
            "美食": "好好吃饭比什么都重要",
            "川菜": "吃得好就好，少点太辣的伤胃",
            "代码": "工作别太拼，注意休息眼睛",
            "加班": "这么辛苦，明天给你寄好吃的",
            "电影": "有娱乐放松就好，看的什么电影呀",
            "同事": "和同事处得好是福气",
        }
        parent_msg = "今天过得怎么样呀？"
        for kw, msg in parent_msgs.items():
            if kw in entry.content:
                parent_msg = msg
                break

        ae = AnalyzedEntry(
            raw=entry,
            summary=entry.content[:50],
            mood=detected_mood,
            keywords=[k for k in mood_map if k in entry.content],
            highlight=any(kw in entry.content for kw in ["健身", "美食", "跑步", "电影", "川菜"]),
            parent_perspective=parent_msg,
        )
        result.analyzed_entries.append(ae)

    highlights = sum(1 for a in result.analyzed_entries if a.highlight)
    print(f"  ✓ 分析了 {len(result.analyzed_entries)} 条，其中 {highlights} 条亮点")

    # 模拟生成
    print("═══ Agent: Generator 开始生成日报 ═══")
    mood_emojis = {Mood.HAPPY: "😊", Mood.EXCITED: "🎉", Mood.CALM: "😌",
                   Mood.TIRED: "😴", Mood.STRESSED: "😰", Mood.NEUTRAL: "💭"}

    def _mood_emoji(m) -> str:
        return mood_emojis.get(m, "💭")

    report = DailyReport(
        date=today,
        title=f"🌅 今日时光 · {today}",
        greeting="亲爱的爸爸妈妈，晚上好！来看看我今天都做了什么吧～\n",
        highlights=[f"{ae.summary} {_mood_emoji(ae.mood)}" for ae in result.analyzed_entries if ae.highlight],
        timeline=[f"{ae.raw.timestamp.strftime('%H:%M')} {ae.summary}" for ae in result.analyzed_entries],
        mood_summary=f"今天总体心情不错，有{highlights}件开心的事。工作和生活都在正轨上。",
        closing="明天继续加油！你们也要好好照顾自己哦～\n",
        raw_entries_count=len(result.raw_entries),
    )
    result.report = report
    print(f"  ✓ 日报生成完成: {report.title}")

    # 模拟推送
    print("═══ Agent: Pusher 开始推送 ═══")
    print(f"\n{'─' * 40}")
    print(f"  {report.title}")
    print(f"  {report.greeting}")
    if report.highlights:
        print("  📌 亮点:")
        for h in report.highlights:
            print(f"     ✨ {h}")
    print("  🕐 时间线:")
    for t in report.timeline:
        print(f"     · {t}")
    print(f"  💬 {report.mood_summary}")
    print(f"  {report.closing}")
    print(f"{'─' * 40}")
    print(f"  ✓ 日报已生成 (共 {report.raw_entries_count} 条记录)")

    result.push_status = "ok"
    result.elapsed_seconds = time.perf_counter() - t0
    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        demo_input = "今天8点起床去健身房跑步，中午和同事吃了川菜，下午写了3小时代码，晚上看了一部好电影"
    else:
        demo_input = " ".join(sys.argv[1:])

    print(f"\n📝 原始输入: {demo_input}\n")
    result = simulate_pipeline(demo_input)

    if not result.errors:
        print(f"\n✅ 演示完成！总耗时 {result.elapsed_seconds:.2f}s")
        print(f"   4 个 Agent 协作完成: Collector → Analyzer → Generator → Pusher")
