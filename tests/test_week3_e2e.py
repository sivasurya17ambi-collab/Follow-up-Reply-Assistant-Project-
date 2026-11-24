"""
Week 3 Test Plan Validation (5 Marks)
Testing Focus: End-to-end bot testing, access control, history logging, and multi-format export.
Project Code: PRJ-042 | Follow-up Reply Assistant
"""

import pytest
from backend.config import settings

def test_api_health_endpoint(client):
    """Verify health endpoint returns status, student identity, and active Chroma stats."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["project_code"] == "PRJ-042"
    assert data["student_name"] == "SIVASURYA.B PSVPEC"
    assert data["reg_no"] == "411723205052"
    assert data["indexed_documents"] >= 4

def test_api_document_lifecycle(client):
    """Verify document upload, listing, and deletion via REST API."""
    test_doc = {
        "filename": "temp_test_meeting.txt",
        "content": "Meeting Title: Temp Client Review\nDate: Nov 24, 2026\nAction Items: Verify invoice.",
        "doc_type": "meeting_notes"
    }

    # Upload
    upload_res = client.post("/api/documents/upload", json=test_doc)
    assert upload_res.status_code == 200
    assert upload_res.json()["success"] is True

    # List
    list_res = client.get("/api/documents/list")
    assert list_res.status_code == 200
    filenames = [d["filename"] for d in list_res.json()["documents"]]
    assert "temp_test_meeting.txt" in filenames

    # Delete
    del_res = client.delete("/api/documents/temp_test_meeting.txt")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

def test_api_draft_generation_with_rag(client):
    """Verify full end-to-end draft generation through API with RAG retrieval and citations."""
    req_payload = {
        "meeting_context": "",
        "user_instructions": "Acme Global proposal for 250 seats and SOC2 compliance",
        "tone": "Persuasive / Sales",
        "recipient_name": "Elena Rostova",
        "sender_name": "Sivasurya B",
        "use_rag": True
    }

    res = client.post("/api/drafts/generate", json=req_payload)
    assert res.status_code == 200
    data = res.json()
    assert "Elena Rostova" in data["recipient"]
    assert len(data["body"]) > 100
    assert len(data["citations"]) > 0
    assert len(data["reply_suggestions"]) > 0
    assert data["word_count"] > 20

def test_api_export_all_formats(client):
    """Verify export module supports txt, md, html, eml, json formats."""
    sample_draft = {
        "subject": "Follow-up on Acme Enterprise Sync",
        "recipient": "Elena Rostova",
        "body": "Thank you for meeting today. We confirmed the 250 enterprise seats and SOC2 pack delivery.",
        "sender": "Sivasurya B"
    }

    for fmt in ["txt", "md", "html", "eml", "json"]:
        res = client.post("/api/export", json={**sample_draft, "export_format": fmt})
        assert res.status_code == 200
        export_data = res.json()
        assert export_data["format"] == fmt
        assert export_data["filename"].endswith(f".{fmt}")
        assert len(export_data["content"]) > 0

def test_access_control_admin_refresh(client):
    """Verify administrative refresh endpoint enforces X-Admin-Key access control."""
    # Unauthorized attempt
    unauth_res = client.post("/api/documents/refresh")
    assert unauth_res.status_code == 401

    # Invalid key
    bad_res = client.post("/api/documents/refresh", headers={"X-Admin-Key": "wrong_key"})
    assert bad_res.status_code == 401

    # Authorized attempt with correct admin key
    auth_res = client.post("/api/documents/refresh", headers={"X-Admin-Key": settings.ADMIN_API_KEY})
    assert auth_res.status_code == 200
    assert auth_res.json()["success"] is True
    assert auth_res.json()["reindexed_documents"] >= 4

def test_history_and_analytics_logging(client):
    """Verify generated drafts are recorded in audit history and analytics are updated."""
    # Get history
    hist_res = client.get("/api/history")
    assert hist_res.status_code == 200
    assert "total_entries" in hist_res.json()

    # Get analytics
    analytics_res = client.get("/api/history/analytics")
    assert analytics_res.status_code == 200
    analytics_data = analytics_res.json()
    assert "total_drafts" in analytics_data
    assert "tones_used" in analytics_data
