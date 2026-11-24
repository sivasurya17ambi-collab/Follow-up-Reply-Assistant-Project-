"""
Template Library Manager
Project Code: PRJ-042 | Follow-up Reply Assistant
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from backend.config import settings

class TemplateLibrary:
    """Manages pre-built and custom follow-up email templates."""

    def __init__(self, template_dir: Optional[Path] = None):
        self.template_dir = template_dir or settings.TEMPLATE_DIR
        self.template_file = self.template_dir / "default_templates.json"
        self.templates: Dict[str, Dict[str, Any]] = {}
        self.load_templates()

    def load_templates(self):
        """Loads templates from JSON file."""
        if self.template_file.exists():
            try:
                data = json.loads(self.template_file.read_text(encoding="utf-8"))
                self.templates = {tpl["id"]: tpl for tpl in data}
            except Exception as e:
                print(f"Error loading templates: {e}")
                self._load_fallback_defaults()
        else:
            self._load_fallback_defaults()
            self.save_templates()

    def _load_fallback_defaults(self):
        self.templates = {
            "tpl_post_meeting": {
                "id": "tpl_post_meeting",
                "name": "Post-Meeting Minutes & Action Items",
                "category": "Meeting Recap",
                "description": "Comprehensive follow-up summarizing meeting discussion, agreed decisions, individual responsibilities, and deadlines.",
                "subject_template": "Follow-up & Action Items: {meeting_title} - {date}",
                "default_tone": "Professional",
                "structure": [
                    "Appreciation for time and participation",
                    "Executive summary of core discussion points",
                    "Action items table with owner and deadline",
                    "Upcoming milestone / next sync date",
                    "Polite closing and invitation for clarifications"
                ]
            },
            "tpl_sales_discovery": {
                "id": "tpl_sales_discovery",
                "name": "Sales Discovery Follow-up & Next Steps",
                "category": "Sales & Leads",
                "description": "Engaging sales follow-up addressing customer pain points, confirming requirements, and proposing next demo or proposal review.",
                "subject_template": "Next steps from our discussion | {client_name} & {company_name}",
                "default_tone": "Persuasive / Sales",
                "structure": [
                    "Thanking lead for sharing challenges and goals",
                    "Recap of key challenges identified (pain points)",
                    "How our proposed solution fits their timeline and scale",
                    "Agreed next milestone (demo / proposal review)",
                    "Direct call-to-action for scheduling"
                ]
            }
        }

    def save_templates(self):
        """Persists current templates to JSON file."""
        try:
            self.template_dir.mkdir(parents=True, exist_ok=True)
            self.template_file.write_text(
                json.dumps(list(self.templates.values()), indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            print(f"Error saving templates: {e}")

    def list_templates(self) -> List[Dict[str, Any]]:
        """Returns all available templates."""
        return list(self.templates.values())

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Fetches a specific template by ID."""
        return self.templates.get(template_id)

    def create_template(self, name: str, category: str, description: str, 
                        subject_template: str, default_tone: str, structure: List[str]) -> Dict[str, Any]:
        """Creates a new custom template and persists it."""
        clean_id = "tpl_" + name.lower().replace(" ", "_").replace("-", "_")[:24]
        new_tpl = {
            "id": clean_id,
            "name": name,
            "category": category,
            "description": description,
            "subject_template": subject_template,
            "default_tone": default_tone,
            "structure": structure
        }
        self.templates[clean_id] = new_tpl
        self.save_templates()
        return new_tpl

# Global singleton
template_library = TemplateLibrary()
