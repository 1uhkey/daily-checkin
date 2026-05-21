from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EntryType(str, Enum):
    TEXT = "text"
    VOICE = "voice"
    PHOTO = "photo"
    VIDEO = "video"


class Mood(str, Enum):
    HAPPY = "happy"
    CALM = "calm"
    TIRED = "tired"
    STRESSED = "stressed"
    EXCITED = "excited"
    NEUTRAL = "neutral"


class RawEntry(BaseModel):
    """Single input collected throughout the day."""

    id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S%f"))
    timestamp: datetime = Field(default_factory=datetime.now)
    type: EntryType = EntryType.TEXT
    content: str
    location: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class AnalyzedEntry(BaseModel):
    """An enriched entry after analysis."""

    raw: RawEntry
    summary: str
    mood: Mood = Mood.NEUTRAL
    keywords: list[str] = Field(default_factory=list)
    highlight: bool = False
    parent_perspective: str = ""


class DailyReport(BaseModel):
    """Final daily report ready for parents."""

    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    title: str = ""
    greeting: str = ""
    highlights: list[str] = Field(default_factory=list)
    timeline: list[str] = Field(default_factory=list)
    photos_note: str = ""
    mood_summary: str = ""
    closing: str = ""
    raw_entries_count: int = 0
    generated_at: datetime = Field(default_factory=datetime.now)


class OrchestrationResult(BaseModel):
    """Complete result of a daily check-in run."""

    raw_entries: list[RawEntry] = Field(default_factory=list)
    analyzed_entries: list[AnalyzedEntry] = Field(default_factory=list)
    report: Optional[DailyReport] = None
    push_status: str = "not_attempted"
    elapsed_seconds: float = 0.0
    errors: list[str] = Field(default_factory=list)
