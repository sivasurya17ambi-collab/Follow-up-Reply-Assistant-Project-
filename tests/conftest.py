"""
Pytest Configuration and Fixtures
Project Code: PRJ-042 | Follow-up Reply Assistant
"""

import sys
from pathlib import Path
import pytest

# Ensure root directory is on Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from backend.main import app
from backend.rag_engine import rag_engine

@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_knowledge_base():
    """Ensure knowledge base has sample documents indexed for tests."""
    rag_engine.reindex_all_sample_documents()
    yield
