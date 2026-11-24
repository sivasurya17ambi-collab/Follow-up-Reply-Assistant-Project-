"""
Week 1 Test Plan Validation (5 Marks)
Testing Focus: Document loading, chunking, and baseline question-answer flow on sample queries.
Project Code: PRJ-042 | Follow-up Reply Assistant
"""

import pytest
from backend.document_parser import DocumentParser
from backend.rag_engine import rag_engine

def test_document_parser_text_and_metadata():
    """Verify metadata extraction for titles, dates, attendees from meeting notes."""
    parser = DocumentParser(chunk_size=300, chunk_overlap=50)
    sample_text = (
        "Meeting Title: Sprint 24 Architecture Sync\n"
        "Date: November 12, 2026\n"
        "Attendees: Alex Mercer, Sarah Jenkins, David Chen\n\n"
        "Discussion: We reviewed billing engine progress and verified latency reduction."
    )

    clean_text, meta = parser.extract_text_and_metadata("sprint_sync.txt", sample_text)
    assert meta["filename"] == "sprint_sync.txt"
    assert "Sprint 24 Architecture Sync" in meta["title"]
    assert "November 12, 2026" in meta["meeting_date"]
    assert "Alex Mercer" in meta["attendees"]
    assert meta["type"] == "meeting_transcript"

def test_document_parser_chunking_and_overlap():
    """Verify recursive chunking splits text without breaking words and creates valid IDs."""
    parser = DocumentParser(chunk_size=200, chunk_overlap=40)
    long_text = (
        "Section 1: Initial discussion regarding database migration.\n\n"
        "Section 2: Detailed analysis of payment gateway performance and retry strategies.\n\n"
        "Section 3: Agreed action items for the frontend engineering team to ship the staging build."
    )

    chunks = parser.chunk_text(long_text, "test_doc.txt", {"doc_type": "meeting_notes"})
    assert len(chunks) >= 2
    for chunk in chunks:
        assert "chunk_id" in chunk
        assert "chunk_index" in chunk
        assert chunk["filename"] == "test_doc.txt"
        assert len(chunk["content"]) > 0

def test_sample_documents_indexed_in_chroma():
    """Verify sample documents are indexed into the Chroma collection."""
    docs = rag_engine.get_indexed_documents()
    assert len(docs) >= 4
    filenames = [d["filename"] for d in docs]
    assert "sales_discovery_acme.txt" in filenames
    assert "q3_product_sync.txt" in filenames
    assert "client_status_onboarding.txt" in filenames
    assert "enterprise_renewal_lead.txt" in filenames

def test_baseline_vector_query():
    """Verify baseline question-answer retrieval on sample queries."""
    results = rag_engine.query_context("billing engine microservices migration", top_k=2)
    assert len(results) > 0
    top_hit = results[0]
    assert "source_doc" in top_hit
    assert "snippet" in top_hit
    assert top_hit["relevance_score"] >= 0.0
