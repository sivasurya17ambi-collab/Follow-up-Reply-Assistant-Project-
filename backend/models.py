"""
Pydantic Schemas for Request/Response Validation
Project Code: PRJ-042 | Follow-up Reply Assistant
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

# ----------------- Document & Knowledge Base Models -----------------

class DocumentChunk(BaseModel):
    chunk_id: str
    doc_name: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DocumentUploadRequest(BaseModel):
    filename: str
    content: str
    doc_type: Optional[str] = "meeting_notes"  # meeting_notes, lead_transcript, email_thread, crm_note
    metadata: Optional[Dict[str, Any]] = None

class DocumentUploadResponse(BaseModel):
    success: bool
    filename: str
    chunks_created: int
    message: str

class IndexedDocumentInfo(BaseModel):
    filename: str
    doc_type: str
    chunks_count: int
    sample_preview: str

class DocumentListResponse(BaseModel):
    total_documents: int
    total_chunks: int
    documents: List[IndexedDocumentInfo]

# ----------------- Citation & RAG Models -----------------

class Citation(BaseModel):
    source_doc: str
    chunk_index: int
    relevance_score: float
    snippet: str

# ----------------- Draft Generation Models -----------------

class DraftGenerateRequest(BaseModel):
    meeting_context: Optional[str] = Field(
        default="", 
        description="Raw meeting notes, transcript, or lead context. If empty, RAG will search the knowledge base using the prompt."
    )
    user_instructions: Optional[str] = Field(
        default="",
        description="Specific instructions e.g. 'Emphasize the API deadline and ask for a 15-minute call'."
    )
    tone: str = Field(
        default="Professional",
        description="Preset: Professional, Friendly / Warm, Urgent / Action-Oriented, Executive / Concise, Persuasive / Sales, Polite Re-engagement"
    )
    template_id: Optional[str] = Field(
        default=None,
        description="ID of template to base the draft on (e.g. tpl_post_meeting, tpl_sales_discovery)"
    )
    recipient_name: Optional[str] = "Colleague / Client"
    sender_name: Optional[str] = "Sivasurya B"
    use_rag: bool = Field(default=True, description="Whether to query the Chroma vector store for additional context")
    llm_provider: Optional[str] = None  # None to use config default

class DraftGenerateResponse(BaseModel):
    subject: str
    recipient: str
    body: str
    tone: str
    template_applied: Optional[str] = None
    citations: List[Citation] = Field(default_factory=list)
    reply_suggestions: List[str] = Field(default_factory=list)
    word_count: int
    reading_time_seconds: int
    generated_at: str

# ----------------- Reply Suggestions Models -----------------

class ReplySuggestionRequest(BaseModel):
    context: str
    tone: Optional[str] = "Professional"
    category: Optional[str] = "general"

class ReplySuggestionItem(BaseModel):
    label: str
    action_type: str  # schedule, send_quote, resolve_blocker, follow_up_nudge, close_deal
    sample_text: str

class ReplySuggestionResponse(BaseModel):
    suggestions: List[ReplySuggestionItem]

# ----------------- Template Models -----------------

class TemplateItem(BaseModel):
    id: str
    name: str
    category: str
    description: str
    subject_template: str
    default_tone: str
    structure: List[str]

class TemplateListResponse(BaseModel):
    count: int
    templates: List[TemplateItem]

class TemplateCreateRequest(BaseModel):
    name: str
    category: str
    description: str
    subject_template: str
    default_tone: str
    structure: List[str]

# ----------------- Export Models -----------------

class ExportRequest(BaseModel):
    subject: str
    recipient: str
    body: str
    export_format: str = Field(..., description="txt, md, html, eml, json")
    sender: Optional[str] = "Sivasurya B"

class ExportResponse(BaseModel):
    format: str
    filename: str
    content: str
    mime_type: str

# ----------------- History & Audit Models -----------------

class HistoryItem(BaseModel):
    id: str
    timestamp: str
    subject: str
    recipient: str
    tone: str
    template_name: Optional[str] = None
    body_preview: str
    citations_count: int
    word_count: int

class HistoryResponse(BaseModel):
    total_entries: int
    items: List[HistoryItem]

# ----------------- System & Health Models -----------------

class HealthResponse(BaseModel):
    status: str
    project_code: str
    project_name: str
    student_name: str
    reg_no: str
    department: str
    version: str
    llm_provider: str
    chroma_status: str
    indexed_documents: int
    indexed_chunks: int

class AdminRefreshResponse(BaseModel):
    success: bool
    reindexed_documents: int
    total_chunks: int
    message: str
