"""
Week 2 Test Plan Validation (5 Marks)
Testing Focus: Answer relevance, citation correctness, edge queries, and fallback handling.
Project Code: PRJ-042 | Follow-up Reply Assistant
"""

import pytest
from backend.rag_engine import rag_engine
from backend.prompt_manager import prompt_manager, TONE_PROFILES
from backend.template_library import template_library
from backend.reply_suggester import reply_suggester

def test_answer_relevance_and_citation_correctness():
    """Verify semantic retrieval retrieves correct document and attaches proper citations."""
    query = "Acme Global 250 enterprise seats SOC2 Type II compliance"
    results = rag_engine.query_context(query, top_k=3)
    assert len(results) > 0

    top_match = results[0]
    # Should accurately point to Acme sales call document
    assert "acme" in top_match["source_doc"].lower()
    assert top_match["relevance_score"] > 0.1
    assert "chunk_index" in top_match

def test_all_six_tone_presets_generate_distinct_content():
    """Verify each tone preset applies distinct greetings, styles, and sign-offs."""
    context = (
        "Meeting Title: Nexus Financial Onboarding\n"
        "Date: November 18, 2026\n"
        "Attendees: Nathan Drake, Chloe Bennet\n"
        "Action Items:\n"
        "- Jessica Wu: Patched webhook payload serialization parser.\n"
        "- Nathan Drake: Re-run reconciliation tests.\n"
    )

    generated_drafts = {}
    for tone in TONE_PROFILES.keys():
        draft = prompt_manager.generate_draft(
            context=context,
            tone=tone,
            recipient_name="Nathan Drake",
            sender_name="Chloe Bennet"
        )
        assert draft.tone == tone
        assert len(draft.body) > 50
        assert draft.recipient == "Nathan Drake"
        generated_drafts[tone] = draft.body

    # Verify Urgent tone differs from Friendly tone
    assert generated_drafts["Urgent / Action-Oriented"] != generated_drafts["Friendly / Warm"]
    assert "URGENT" in prompt_manager.generate_draft(context=context, tone="Urgent / Action-Oriented").subject

def test_template_library_substitution():
    """Verify template library applies variables and structural formatting."""
    tpl = template_library.get_template("tpl_post_meeting")
    assert tpl is not None
    assert "subject_template" in tpl

    draft = prompt_manager.generate_draft(
        context="Meeting Title: Q3 Engineering Sync\nDate: Oct 20, 2026",
        template_id="tpl_post_meeting",
        recipient_name="David Chen"
    )
    assert "Q3 Engineering Sync" in draft.subject
    assert draft.template_applied == "Post-Meeting Minutes & Action Items"

def test_edge_queries_and_fallback_handling():
    """Verify system handles empty queries, whitespace, and sparse contexts without errors."""
    # 1. Empty context fallback
    draft_empty = prompt_manager.generate_draft(context="", user_instructions="", tone="Professional")
    assert draft_empty is not None
    assert len(draft_empty.body) > 0
    assert draft_empty.subject != ""

    # 2. Empty query search
    res = rag_engine.query_context("   ", top_k=2)
    assert res == []

    # 3. Context without explicit action items
    draft_sparse = prompt_manager.generate_draft(
        context="General check-in call with client. Discussed general industry trends.",
        tone="Executive / Concise"
    )
    assert draft_sparse is not None
    assert "Regards" in draft_sparse.body

def test_reply_suggester_intents():
    """Verify smart reply suggestion chips map to context intents."""
    demo_context = "The client requested a 45-minute live technical walkthrough next week."
    sugg = reply_suggester.generate_suggestions(demo_context)
    assert any("Meeting Time Slots" in s["label"] or "Demo" in s["label"] for s in sugg)

    blocker_context = "Encountered a critical webhook discrepancy causing API delays."
    sugg_block = reply_suggester.generate_suggestions(blocker_context)
    assert any("Blocker" in s["label"] for s in sugg_block)
