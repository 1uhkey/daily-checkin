"""Tests for multi-agent pipeline — uses mock to avoid API calls."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.models.schemas import (
    AnalyzedEntry,
    DailyReport,
    EntryType,
    Mood,
    RawEntry,
)


class TestRawEntry:
    def test_create_entry(self):
        entry = RawEntry(content="早起跑步30分钟", tags=["运动", "晨间"])
        assert entry.type == EntryType.TEXT
        assert len(entry.tags) == 2
        assert entry.id != ""

    def test_entry_defaults(self):
        entry = RawEntry(content="测试")
        assert entry.location is None
        assert entry.tags == []


class TestAnalyzedEntry:
    def test_create_analyzed(self):
        raw = RawEntry(content="和朋友聚餐")
        analyzed = AnalyzedEntry(
            raw=raw,
            summary="和朋友们吃了一顿开心的饭",
            mood=Mood.HAPPY,
            keywords=["聚餐", "社交"],
            highlight=True,
            parent_perspective="今天和朋友们聚餐了，有好好吃饭，妈妈放心了",
        )
        assert analyzed.highlight is True
        assert analyzed.mood == Mood.HAPPY


class TestDailyReport:
    def test_report_creation(self):
        report = DailyReport(
            date="2026-05-21",
            title="🌅 小明的今日时光",
            greeting="亲爱的爸爸妈妈，这是我今天的日报～",
            highlights=["去健身房运动了1小时", "中午吃了好吃的川菜"],
            timeline=["08:00 起床晨跑", "12:00 和同事吃川菜"],
            mood_summary="今天整体心情不错，工作有进展",
            closing="明天也要加油，爱你们！",
            raw_entries_count=5,
        )
        assert len(report.highlights) == 2
        assert len(report.timeline) == 2
        assert report.raw_entries_count == 5


class TestOrchestrationResult:
    def test_empty_result(self):
        from src.models.schemas import OrchestrationResult

        result = OrchestrationResult()
        assert result.raw_entries == []
        assert result.report is None
        assert result.push_status == "not_attempted"


class TestCollectorAgentInit:
    def test_agent_name(self):
        from src.agents import CollectorAgent

        client = MagicMock()
        agent = CollectorAgent(client)
        assert agent.name == "Collector"


class TestAnalyzerAgentInit:
    def test_agent_name(self):
        from src.agents import AnalyzerAgent

        client = MagicMock()
        agent = AnalyzerAgent(client)
        assert agent.name == "Analyzer"


class TestGeneratorAgentInit:
    def test_agent_name(self):
        from src.agents import GeneratorAgent

        client = MagicMock()
        agent = GeneratorAgent(client)
        assert agent.name == "Generator"


class TestPusherAgentInit:
    def test_agent_name(self):
        from src.agents import PusherAgent

        client = MagicMock()
        agent = PusherAgent(client)
        assert agent.name == "Pusher"
