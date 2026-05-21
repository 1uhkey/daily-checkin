from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Optional

from ..models.schemas import DailyReport, OrchestrationResult


class Journal:
    """Local JSON-based storage for daily check-in records."""

    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def save_result(self, result: OrchestrationResult) -> str:
        date = datetime.now().strftime("%Y-%m-%d")
        path = os.path.join(self.base_dir, f"checkin-{date}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result.model_dump_json(indent=2), f, ensure_ascii=False)
        return path

    def load_result(self, date: str) -> Optional[OrchestrationResult]:
        path = os.path.join(self.base_dir, f"checkin-{date}.json")
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as f:
            return OrchestrationResult.model_validate_json(f.read())
