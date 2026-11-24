"""
Contextual Reply Suggestions Module
Project Code: PRJ-042 | Follow-up Reply Assistant
"""

import re
from typing import List, Dict, Any

class ReplySuggester:
    """Generates next-action suggestions, smart reply chips, and follow-up prompts based on meeting context."""

    def generate_suggestions(self, context: str, tone: str = "Professional") -> List[Dict[str, str]]:
        lower_ctx = (context or "").lower()
        suggestions: List[Dict[str, str]] = []

        # 1. Check for Demo / Scheduling intent
        if any(w in lower_ctx for w in ["demo", "walkthrough", "next sync", "call", "schedule", "calendar"]):
            suggestions.append({
                "label": "📅 Propose 2-3 Meeting Time Slots",
                "action_type": "schedule",
                "sample_text": "Would Tuesday at 2:00 PM EST or Thursday at 11:00 AM EST work best for our 45-minute sync?"
            })

        # 2. Check for Pricing / Budget / Proposal intent
        if any(w in lower_ctx for w in ["budget", "pricing", "quote", "cost", "proposal", "discount", "seats"]):
            suggestions.append({
                "label": "💼 Attach Enterprise Pricing & ROI Model",
                "action_type": "send_quote",
                "sample_text": "I have attached our customized multi-tier pricing and ROI analysis reflecting the 250 enterprise seats."
            })

        # 3. Check for Blockers / Technical Issues
        if any(w in lower_ctx for w in ["blocker", "delay", "bug", "webhook", "incident", "discrepancy", "error", "failing"]):
            suggestions.append({
                "label": "⚡ Request Blocker Resolution Sync",
                "action_type": "resolve_blocker",
                "sample_text": "Our engineering lead has deployed a hotfix; please let us know if we can run a 15-minute verification sync today."
            })

        # 4. Check for Action Items / Deadlines
        if any(w in lower_ctx for w in ["action item", "deadline", "by friday", "by monday", "due", "eod"]):
            suggestions.append({
                "label": "⏱️ Send Milestone Check-in Nudge",
                "action_type": "follow_up_nudge",
                "sample_text": "Following up to confirm that action item deliverables remain on track for this Friday's target."
            })

        # 5. Check for Security / Compliance / Contracts
        if any(w in lower_ctx for w in ["soc2", "iso", "compliance", "security", "contract", "legal", "nda", "sign"]):
            suggestions.append({
                "label": "🔒 Share Security Whitepaper & SOC2 Pack",
                "action_type": "share_compliance",
                "sample_text": "Please find attached our latest SOC2 Type II audit report and architecture security whitepaper for your IT team."
            })

        # 6. Check for Contract Renewal / Expansion
        if any(w in lower_ctx for w in ["renewal", "expansion", "annual", "expire", "add-on"]):
            suggestions.append({
                "label": "✍️ Request Renewal Sign-Off Review",
                "action_type": "close_deal",
                "sample_text": "We are ready to apply the early sign-off 10% multi-year incentive once your CFO completes the review."
            })

        # Fallback general suggestions if few were matched
        if len(suggestions) < 3:
            general_pool = [
                {
                    "label": "🤝 Request Executive Feedback / Comments",
                    "action_type": "feedback",
                    "sample_text": "Please let me know if there are any additional adjustments or priorities you would like us to incorporate."
                },
                {
                    "label": "📎 Offer Additional Reference Materials",
                    "action_type": "resources",
                    "sample_text": "Happy to share our technical integration case study if that helps your team's evaluation."
                },
                {
                    "label": "☕ Schedule Informal Touchpoint",
                    "action_type": "catchup",
                    "sample_text": "Let's grab a quick 10-minute check-in next week to ensure everything continues smoothly."
                }
            ]
            for item in general_pool:
                if len(suggestions) >= 4:
                    break
                if item["label"] not in [s["label"] for s in suggestions]:
                    suggestions.append(item)

        return suggestions[:4]

# Global singleton
reply_suggester = ReplySuggester()
