"""
Prompt Tuning, Tone Presets & Context-Aware Generation Engine (Week 2 Requirement)
Project Code: PRJ-042 | Follow-up Reply Assistant
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from backend.config import settings
from backend.models import Citation, DraftGenerateResponse
from backend.template_library import template_library
from backend.reply_suggester import reply_suggester

TONE_PROFILES = {
    "Professional": {
        "greeting": "Hi {recipient},",
        "intro": "Thank you for taking the time to meet regarding {topic}.",
        "tone_guidance": "Clear, courteous, objective, and structured with distinct action items.",
        "signoff": "Best regards,\n{sender}\nFollow-up Reply Assistant | PRJ-042"
    },
    "Friendly / Warm": {
        "greeting": "Hey {recipient},",
        "intro": "It was truly great speaking with you earlier regarding {topic}! I really appreciated our productive discussion.",
        "tone_guidance": "Collaborative, warm, encouraging, highlighting shared progress and mutual excitement.",
        "signoff": "Warmly,\n{sender}\nFollow-up Reply Assistant | PRJ-042"
    },
    "Urgent / Action-Oriented": {
        "greeting": "Dear {recipient},",
        "intro": "I am following up directly on the critical milestones and action items from our recent sync on {topic}.",
        "tone_guidance": "Direct, priority-driven, emphasizing deadlines, open blockers, and immediate decision requirements.",
        "signoff": "Sincerely,\n{sender}\nFollow-up Reply Assistant | PRJ-042"
    },
    "Executive / Concise": {
        "greeting": "{recipient},",
        "intro": "Bottom Line Up Front (BLUF): Below is the executive recap and action roadmap from our sync on {topic}.",
        "tone_guidance": "High-impact, zero fluff, concise bullet points, highlighting financial or timeline impact.",
        "signoff": "Regards,\n{sender}\nPRJ-042"
    },
    "Persuasive / Sales": {
        "greeting": "Hello {recipient},",
        "intro": "Thank you for sharing your team's current strategic priorities and operational goals around {topic}.",
        "tone_guidance": "Value-oriented, focused on ROI, addressing technical risks, and driving momentum toward the next evaluation milestone.",
        "signoff": "Looking forward to partnering,\n{sender}\nEnterprise Solutions | PRJ-042"
    },
    "Polite Re-engagement": {
        "greeting": "Hi {recipient},",
        "intro": "I hope you are having a productive week! I know things get remarkably busy, so I wanted to share a gentle check-in regarding {topic}.",
        "tone_guidance": "Low-pressure, considerate, helpful, leaving the door open for quick touchpoints.",
        "signoff": "Best wishes,\n{sender}\nPRJ-042"
    }
}

class PromptManager:
    """Manages prompt construction, tone presets, and draft generation."""

    def __init__(self):
        self.tones = TONE_PROFILES

    def get_supported_tones(self) -> List[str]:
        return list(self.tones.keys())

    def _extract_entities_from_context(self, context: str) -> Dict[str, Any]:
        """Extracts structured entities (title, date, attendees, action items, blockers) from raw text."""
        entities = {
            "title": "Meeting Sync",
            "date": datetime.now().strftime("%B %d, %Y"),
            "attendees": [],
            "action_items": [],
            "blockers": [],
            "key_points": []
        }

        if not context:
            return entities

        # Title
        title_m = re.search(r"(?:Meeting Title|Subject|Topic):\s*([^\n]+)", context, re.IGNORECASE)
        if title_m:
            entities["title"] = title_m.group(1).strip()
        else:
            first_line = context.strip().split("\n")[0]
            if len(first_line) < 80:
                entities["title"] = first_line.replace("#", "").strip()

        # Date
        date_m = re.search(r"Date:\s*([^\n]+)", context, re.IGNORECASE)
        if date_m:
            entities["date"] = date_m.group(1).strip()

        # Attendees
        att_m = re.search(r"Attendees?:\s*([^\n]+)", context, re.IGNORECASE)
        if att_m:
            raw_att = att_m.group(1).strip()
            entities["attendees"] = [a.strip() for a in re.split(r"[,;]", raw_att) if a.strip()]

        # Action Items extraction
        lines = context.split("\n")
        in_action_section = False
        in_blocker_section = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            lower_line = stripped.lower()
            if "action items" in lower_line or "agreed next steps" in lower_line or "commitments" in lower_line:
                in_action_section = True
                in_blocker_section = False
                continue
            elif "blockers" in lower_line or "concerns" in lower_line or "objections" in lower_line:
                in_blocker_section = True
                in_action_section = False
                continue
            elif any(header in lower_line for header in ["next sync", "next steps", "discussion", "highlights"]):
                in_action_section = False
                in_blocker_section = False

            if in_action_section:
                if stripped.startswith(("-", "*", "•")) or re.match(r"^\d+\.", stripped):
                    item = re.sub(r"^[-*•\d.]+\s*", "", stripped)
                    entities["action_items"].append(item)
                elif ":" in stripped and len(stripped) < 160:
                    entities["action_items"].append(stripped)

            elif in_blocker_section:
                if stripped.startswith(("-", "*", "•")) or re.match(r"^\d+\.", stripped):
                    item = re.sub(r"^[-*•\d.]+\s*", "", stripped)
                    entities["blockers"].append(item)

            elif stripped.startswith(("-", "*", "•")) and not in_action_section:
                item = re.sub(r"^[-*•\d.]+\s*", "", stripped)
                if len(item) > 15:
                    entities["key_points"].append(item)

        # Fallback if no specific action items found
        if not entities["action_items"] and entities["key_points"]:
            entities["action_items"] = entities["key_points"][:3]

        return entities

    def generate_draft(
        self,
        context: str,
        user_instructions: str = "",
        tone: str = "Professional",
        template_id: Optional[str] = None,
        recipient_name: str = "Team / Partner",
        sender_name: str = "Sivasurya B",
        citations: Optional[List[Citation]] = None,
        provider: Optional[str] = None
    ) -> DraftGenerateResponse:
        """
        Generates a tailored follow-up draft using tone presets, template constraints,
        and extracted context or citations.
        """
        selected_tone = tone if tone in self.tones else "Professional"
        tone_profile = self.tones[selected_tone]
        tpl = template_library.get_template(template_id) if template_id else None

        # Try external LLM if configured and keys are set
        active_provider = provider or settings.LLM_PROVIDER
        if active_provider == "openai" and settings.OPENAI_API_KEY:
            try:
                return self._call_openai_llm(
                    context, user_instructions, selected_tone, tpl, recipient_name, sender_name, citations
                )
            except Exception as e:
                print(f"OpenAI LLM error, falling back to context-aware engine: {e}")

        # Deterministic Context-Aware Generation Engine
        entities = self._extract_entities_from_context(context)
        topic = entities["title"]
        date_str = entities["date"]

        # Subject line generation
        if tpl and "subject_template" in tpl:
            subject = tpl["subject_template"].format(
                meeting_title=topic,
                date=date_str,
                client_name=recipient_name,
                company_name="Acme Global" if "acme" in context.lower() else "Enterprise Partner",
                topic=topic,
                project_name=topic
            )
        else:
            if selected_tone == "Urgent / Action-Oriented":
                subject = f"URGENT: Key Decisions & Immediate Next Steps - {topic}"
            elif selected_tone == "Executive / Concise":
                subject = f"Executive Recap: {topic} ({date_str})"
            elif selected_tone == "Persuasive / Sales":
                subject = f"Next Steps & Partnership Proposal | {recipient_name} & {topic}"
            else:
                subject = f"Follow-up & Agreed Action Items: {topic} - {date_str}"

        # Construct Body
        greeting = tone_profile["greeting"].format(recipient=recipient_name)
        intro = tone_profile["intro"].format(recipient=recipient_name, topic=topic)

        # Key discussion summary
        body_parts = [greeting, intro, ""]

        # User instructions injection if provided
        if user_instructions and user_instructions.strip():
            body_parts.append(f"Special Note: As discussed, {user_instructions.strip()}.\n")

        # Discussion Points
        if entities["key_points"]:
            body_parts.append("### Key Discussion Highlights:")
            for pt in entities["key_points"][:4]:
                body_parts.append(f"• {pt}")
            body_parts.append("")

        # Action Items / Ownership Table
        if entities["action_items"]:
            body_parts.append("### Agreed Action Items & Responsibilities:")
            for idx, ai in enumerate(entities["action_items"][:5], 1):
                body_parts.append(f"{idx}. {ai}")
            body_parts.append("")

        # Blockers / Risks if present
        if entities["blockers"]:
            body_parts.append("### Open Blockers & Resolution Plan:")
            for b in entities["blockers"][:3]:
                body_parts.append(f"⚠️ {b}")
            body_parts.append("")

        # Next Steps & Closing
        if selected_tone == "Executive / Concise":
            body_parts.append("Next Checkpoint: Please review the items above by EOD Wednesday. I will provide the next milestone telemetry accordingly.\n")
        elif selected_tone == "Persuasive / Sales":
            body_parts.append("Please feel free to share the attached architecture and security details with your technical committee. I would be thrilled to lock in Tuesday at 2:00 PM EST for our live technical session.\n")
        elif selected_tone == "Urgent / Action-Oriented":
            body_parts.append("Given our tight production timelines, your prompt confirmation on these items by tomorrow at 3:00 PM is essential to avoid milestone delays.\n")
        elif selected_tone == "Polite Re-engagement":
            body_parts.append("Whenever you have a few minutes, let me know if the proposed schedule aligns with your availability, or if you'd prefer to connect next week.\n")
        else:
            body_parts.append("Please let me know if any adjustments or additions are required before we reconvene for our next sync.\n")

        signoff = tone_profile["signoff"].format(sender=sender_name)
        body_parts.append(signoff)

        full_body = "\n".join(body_parts)

        # Citations handling
        actual_citations = citations or []

        # Smart reply suggestions
        suggestions_data = reply_suggester.generate_suggestions(context, selected_tone)
        suggestion_labels = [s["label"] for s in suggestions_data]

        word_count = len(full_body.split())
        reading_time = max(1, round(word_count / 180 * 60))

        return DraftGenerateResponse(
            subject=subject,
            recipient=recipient_name,
            body=full_body,
            tone=selected_tone,
            template_applied=tpl["name"] if tpl else None,
            citations=actual_citations,
            reply_suggestions=suggestion_labels,
            word_count=word_count,
            reading_time_seconds=reading_time,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def _call_openai_llm(self, context, user_instructions, tone, tpl, recipient_name, sender_name, citations):
        """Invoke OpenAI API when key is configured."""
        import openai
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        system_prompt = (
            "You are an elite Business Follow-up Reply Assistant (Project PRJ-042). "
            f"Write an email in a {tone} tone. "
            "Structure the response clearly with Subject: on the first line, followed by the email body. "
            "Ensure agreed action items, blockers, and next steps are highlighted."
        )

        user_prompt = f"Recipient: {recipient_name}\nSender: {sender_name}\n\nContext:\n{context}\n\nInstructions: {user_instructions}"
        if tpl:
            user_prompt += f"\n\nTemplate Structure to Follow:\n{', '.join(tpl['structure'])}"

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4
        )

        raw_output = response.choices[0].message.content or ""
        lines = raw_output.strip().split("\n")
        subject = f"Follow-up: {topic}"
        body_lines = []

        for line in lines:
            if line.lower().startswith("subject:"):
                subject = line.split(":", 1)[1].strip()
            else:
                body_lines.append(line)

        body = "\n".join(body_lines).strip()
        suggestions_data = reply_suggester.generate_suggestions(context, tone)

        return DraftGenerateResponse(
            subject=subject,
            recipient=recipient_name,
            body=body,
            tone=tone,
            template_applied=tpl["name"] if tpl else None,
            citations=citations or [],
            reply_suggestions=[s["label"] for s in suggestions_data],
            word_count=len(body.split()),
            reading_time_seconds=max(1, round(len(body.split()) / 180 * 60)),
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

# Global singleton
prompt_manager = PromptManager()
