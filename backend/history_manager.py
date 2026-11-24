"""
History & Audit Trail Manager (Week 3 Requirement)
Project Code: PRJ-042 | Follow-up Reply Assistant
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.config import settings

class HistoryManager:
    """Manages audit trail, saved drafts, and session analytics."""

    def __init__(self, history_file: Optional[Path] = None):
        self.history_file = history_file or settings.HISTORY_FILE
        self.records: List[Dict[str, Any]] = []
        self.load_history()

    def load_history(self):
        if self.history_file.exists():
            try:
                data = json.loads(self.history_file.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    self.records = data
            except Exception as e:
                print(f"Error loading history: {e}")
                self.records = []
        else:
            self.records = []

    def save_history(self):
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            self.history_file.write_text(json.dumps(self.records, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"Error saving history: {e}")

    def add_entry(
        self,
        subject: str,
        recipient: str,
        tone: str,
        template_name: Optional[str],
        body: str,
        citations_count: int = 0
    ) -> Dict[str, Any]:
        entry = {
            "id": f"draft_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "subject": subject,
            "recipient": recipient,
            "tone": tone,
            "template_name": template_name or "Custom",
            "body_preview": (body[:140] + "...") if len(body) > 140 else body,
            "full_body": body,
            "citations_count": citations_count,
            "word_count": len(body.split())
        }
        self.records.insert(0, entry)  # Latest first
        if len(self.records) > 200:
            self.records = self.records[:200]
        self.save_history()
        return entry

    def get_entries(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.records[:limit]

    def get_analytics(self) -> Dict[str, Any]:
        total = len(self.records)
        if total == 0:
            return {
                "total_drafts": 0,
                "tones_used": {},
                "average_words": 0,
                "latest_timestamp": "None"
            }

        tones: Dict[str, int] = {}
        total_words = 0
        for r in self.records:
            t = r.get("tone", "Professional")
            tones[t] = tones.get(t, 0) + 1
            total_words += r.get("word_count", 0)

        return {
            "total_drafts": total,
            "tones_used": tones,
            "average_words": round(total_words / total),
            "latest_timestamp": self.records[0]["timestamp"] if self.records else "None"
        }

    def clear(self):
        self.records = []
        self.save_history()

history_manager = HistoryManager()
