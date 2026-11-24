"""
FastAPI Main Application
Project Code: PRJ-042 | Follow-up Reply Assistant
Student: SIVASURYA.B PSVPEC (Reg No: 411723205052)
Department: IT | Category: Email and Reply Assistants
"""

from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List

from backend.config import settings
from backend.models import (
    HealthResponse,
    DocumentUploadRequest,
    DocumentUploadResponse,
    DocumentListResponse,
    DraftGenerateRequest,
    DraftGenerateResponse,
    ReplySuggestionRequest,
    ReplySuggestionResponse,
    ReplySuggestionItem,
    TemplateItem,
    TemplateListResponse,
    TemplateCreateRequest,
    ExportRequest,
    ExportResponse,
    HistoryResponse,
    AdminRefreshResponse,
    Citation
)
from backend.rag_engine import rag_engine
from backend.prompt_manager import prompt_manager, TONE_PROFILES
from backend.template_library import template_library
from backend.reply_suggester import reply_suggester
from backend.export_service import export_service
from backend.history_manager import history_manager

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-reindex sample datasets on initial startup if collection is empty
    try:
        if rag_engine.collection.count() == 0:
            rag_engine.reindex_all_sample_documents()
    except Exception as e:
        print(f"Startup indexing notice: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="GenAI-powered Follow-up Reply Assistant creating reminder and follow-up email drafts from meeting and lead context. (PRJ-042)",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for frontend and API consumers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Access Control / Auth Helper (Week 3) -----------------

def verify_admin_key(x_admin_key: Optional[str] = Header(None)):
    """Simple API-key header validation for administrative refresh actions."""
    if not x_admin_key or x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Admin-Key header for admin operation."
        )
    return True

# ----------------- System & Health Endpoints -----------------

@app.get("/", tags=["System"])
def root_info():
    return {
        "project_code": settings.PROJECT_CODE,
        "project_name": settings.PROJECT_NAME,
        "student_name": settings.STUDENT_NAME,
        "reg_no": settings.REG_NO,
        "department": settings.DEPARTMENT,
        "email": settings.EMAIL,
        "status": "Online",
        "docs_url": "/docs",
        "health_check": "/api/health"
    }

@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def health_check():
    indexed_docs = rag_engine.get_indexed_documents()
    total_chunks = rag_engine.collection.count()
    return HealthResponse(
        status="healthy",
        project_code=settings.PROJECT_CODE,
        project_name=settings.PROJECT_NAME,
        student_name=settings.STUDENT_NAME,
        reg_no=settings.REG_NO,
        department=settings.DEPARTMENT,
        version=settings.APP_VERSION,
        llm_provider=settings.LLM_PROVIDER,
        chroma_status="active",
        indexed_documents=len(indexed_docs),
        indexed_chunks=total_chunks
    )

# ----------------- Knowledge Base & Document Endpoints (Week 1 & 2) -----------------

@app.post("/api/documents/upload", response_model=DocumentUploadResponse, tags=["Knowledge Base"])
def upload_document(req: DocumentUploadRequest):
    if not req.content or not req.content.strip():
        raise HTTPException(status_code=400, detail="Document content cannot be empty.")

    chunks_added = rag_engine.add_document(
        filename=req.filename,
        content=req.content,
        doc_type=req.doc_type or "meeting_notes",
        extra_meta=req.metadata
    )

    return DocumentUploadResponse(
        success=True,
        filename=req.filename,
        chunks_created=chunks_added,
        message=f"Document successfully parsed and indexed into {chunks_added} chunks."
    )

@app.get("/api/documents/list", response_model=DocumentListResponse, tags=["Knowledge Base"])
def list_documents():
    docs = rag_engine.get_indexed_documents()
    return DocumentListResponse(
        total_documents=len(docs),
        total_chunks=rag_engine.collection.count(),
        documents=docs
    )

@app.delete("/api/documents/{filename}", tags=["Knowledge Base"])
def delete_document(filename: str):
    success = rag_engine.delete_document(filename)
    if not success:
        raise HTTPException(status_code=404, detail=f"Document '{filename}' not found.")
    return {"success": True, "message": f"Document '{filename}' deleted from knowledge base."}

@app.post("/api/documents/refresh", response_model=AdminRefreshResponse, tags=["Knowledge Base"])
def admin_refresh_knowledge_base(authorized: bool = Depends(verify_admin_key)):
    """Admin refresh workflow (Week 2 Requirement): Re-indexes all sample datasets into Chroma."""
    result = rag_engine.reindex_all_sample_documents()
    return AdminRefreshResponse(
        success=True,
        reindexed_documents=result["indexed_documents"],
        total_chunks=result["total_chunks"],
        message="Knowledge base successfully refreshed and re-indexed from sample repository."
    )

# ----------------- Draft Generation & RAG Endpoints -----------------

@app.post("/api/drafts/generate", response_model=DraftGenerateResponse, tags=["Draft Generation"])
def generate_draft(req: DraftGenerateRequest):
    context_text = req.meeting_context or ""
    citations: List[Citation] = []

    # If RAG is enabled, retrieve matching context from Chroma
    if req.use_rag:
        search_query = req.user_instructions or context_text[:200]
        if search_query and search_query.strip():
            matched_chunks = rag_engine.query_context(search_query, top_k=settings.RETRIEVAL_TOP_K)
            for m in matched_chunks:
                citations.append(Citation(
                    source_doc=m["source_doc"],
                    chunk_index=m["chunk_index"],
                    relevance_score=m["relevance_score"],
                    snippet=m["snippet"]
                ))
            
            # If no manual context provided, synthesize context from retrieved snippets
            if not context_text.strip() and matched_chunks:
                context_text = "\n\n---\n\n".join([f"[Source: {m['source_doc']}]\n{m['snippet']}" for m in matched_chunks])

    if not context_text.strip():
        # Fallback dummy context if nothing was supplied or retrieved
        context_text = "General Project Sync\nDate: Today\nAction Items: Review project milestones and confirm next sync."

    draft_response = prompt_manager.generate_draft(
        context=context_text,
        user_instructions=req.user_instructions or "",
        tone=req.tone,
        template_id=req.template_id,
        recipient_name=req.recipient_name or "Partner",
        sender_name=req.sender_name or "Sivasurya B",
        citations=citations,
        provider=req.llm_provider
    )

    # Save to history & audit trail (Week 3 Requirement)
    history_manager.add_entry(
        subject=draft_response.subject,
        recipient=draft_response.recipient,
        tone=draft_response.tone,
        template_name=draft_response.template_applied,
        body=draft_response.body,
        citations_count=len(draft_response.citations)
    )

    return draft_response

# ----------------- Reply Suggestions & Presets -----------------

@app.post("/api/suggestions/replies", response_model=ReplySuggestionResponse, tags=["Suggestions"])
def get_reply_suggestions(req: ReplySuggestionRequest):
    suggestions = reply_suggester.generate_suggestions(req.context, req.tone or "Professional")
    items = [
        ReplySuggestionItem(
            label=s["label"],
            action_type=s["action_type"],
            sample_text=s["sample_text"]
        ) for s in suggestions
    ]
    return ReplySuggestionResponse(suggestions=items)

@app.get("/api/tones", tags=["Presets"])
def list_tone_presets():
    return {
        "tones": list(TONE_PROFILES.keys()),
        "details": {
            k: {
                "guidance": v["tone_guidance"],
                "sample_greeting": v["greeting"].format(recipient="Alex")
            }
            for k, v in TONE_PROFILES.items()
        }
    }

# ----------------- Template Library Endpoints -----------------

@app.get("/api/templates", response_model=TemplateListResponse, tags=["Template Library"])
def list_templates():
    tpls = template_library.list_templates()
    items = [
        TemplateItem(
            id=t["id"],
            name=t["name"],
            category=t["category"],
            description=t["description"],
            subject_template=t["subject_template"],
            default_tone=t["default_tone"],
            structure=t["structure"]
        ) for t in tpls
    ]
    return TemplateListResponse(count=len(items), templates=items)

@app.get("/api/templates/{template_id}", response_model=TemplateItem, tags=["Template Library"])
def get_template(template_id: str):
    t = template_library.get_template(template_id)
    if not t:
        raise HTTPException(status_code=404, detail="Template not found.")
    return TemplateItem(**t)

@app.post("/api/templates", response_model=TemplateItem, tags=["Template Library"])
def create_template(req: TemplateCreateRequest):
    new_tpl = template_library.create_template(
        name=req.name,
        category=req.category,
        description=req.description,
        subject_template=req.subject_template,
        default_tone=req.default_tone,
        structure=req.structure
    )
    return TemplateItem(**new_tpl)

# ----------------- Export Module Endpoints (Week 3) -----------------

@app.post("/api/export", response_model=ExportResponse, tags=["Export Module"])
def export_draft(req: ExportRequest):
    result = export_service.export(
        subject=req.subject,
        recipient=req.recipient,
        body=req.body,
        export_format=req.export_format,
        sender=req.sender or "Sivasurya B"
    )
    return ExportResponse(**result)

# ----------------- History & Analytics Endpoints (Week 3) -----------------

@app.get("/api/history", response_model=HistoryResponse, tags=["History & Audit"])
def get_history(limit: int = 50):
    entries = history_manager.get_entries(limit=limit)
    return HistoryResponse(total_entries=len(entries), items=entries)

@app.get("/api/history/analytics", tags=["History & Audit"])
def get_history_analytics():
    return history_manager.get_analytics()

@app.post("/api/history/clear", tags=["History & Audit"])
def clear_history():
    history_manager.clear()
    return {"success": True, "message": "History cleared."}


