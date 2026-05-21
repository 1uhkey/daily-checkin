from __future__ import annotations

import os

from dotenv import load_dotenv


def load_config() -> dict:
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("请在 .env 文件中设置 ANTHROPIC_API_KEY")
    return {
        "api_key": api_key,
        "model": os.getenv("DAILY_CHECKIN_MODEL", "claude-sonnet-4-6"),
        "webhook_url": os.getenv("PUSH_WEBHOOK_URL", ""),
        "email_to": os.getenv("PUSH_EMAIL_TO", ""),
    }
