# 🎓 COMPREHENSIVE VIVA QUESTIONS & ANSWERS GUIDE

## PROJECT CODE: PRJ-042 | FOLLOW-UP REPLY ASSISTANT
**Student:** SIVASURYA.B (Reg No: 411723205052) | **Dept:** Information Technology  

---

### CATEGORY 1: PROJECT OVERVIEW & DOMAIN

#### Q1: What is the main objective of the Follow-up Reply Assistant?
**Answer:** The objective of PRJ-042 is to automate the synthesis of structured, professional follow-up and reminder email drafts from unstructured meeting notes, discovery calls, and CRM lead dialogues. It ensures zero dropped action items, eliminates manual drafting latency, and tailors the communication style using tone presets.

#### Q2: Who are the primary target users for this application?
**Answer:** Enterprise sales executives, project managers, customer success managers, and engineering team leads who conduct frequent syncs and need to distribute accurate recaps and next-step commitments quickly.

#### Q3: What were the key requirements outlined in your project assignment sheet?
**Answer:** The syllabus required:
1. Draft generation from meeting or lead context.
2. Tone presets (e.g. Professional, Friendly, Urgent, Executive, Sales).
3. Contextual reply suggestions / action chips.
4. An extensible template library.
5. An interactive editor with send-ready/export capabilities (.txt, .md, .html, .eml, .json).
6. A 3-week progressive milestone and testing plan evaluated out of 45 marks.

---

### CATEGORY 2: RAG ARCHITECTURE & CHROMA VECTOR DATABASE

#### Q4: What is Retrieval-Augmented Generation (RAG) and why is it used here?
**Answer:** RAG combines information retrieval with generative language modeling. Rather than relying solely on the static weights of an LLM (which may hallucinate or lack private context), RAG searches a specialized vector knowledge base (Chroma) for the most relevant document chunks and feeds them into the generation prompt as factual ground truth with source citations.

#### Q5: Why did you choose Chroma as the vector database over FAISS or Pinecone?
**Answer:** 
1. **Embedded & Persistent:** Chroma runs locally as an embedded database within Python, saving state to disk without needing external Docker containers or paid cloud SaaS subscriptions.
2. **Metadata Filtering:** Chroma supports rich metadata storage alongside vectors, allowing us to filter by document name, attendees, and meeting dates.
3. **Syllabus Recommendation:** Chroma is one of the recommended technologies explicitly specified in the PRJ-042 syllabus (`FastAPI + LangChain + Streamlit + FAISS/Chroma`).

#### Q6: How does the text chunking mechanism work in your project?
**Answer:** In `backend/document_parser.py`, we implement a hierarchical recursive boundary chunker. It splits content first by paragraphs, then by sentences, and finally by words. It uses a chunk size of 400 characters with an overlap of 80 characters. The overlap is critical because it ensures thoughts that span across boundaries are not truncated, preserving semantic continuity during vector similarity search.

#### Q7: How does your embedding function work, and how does it guarantee offline operation?
**Answer:** We implemented a `FastSemanticEmbeddingFunction` in `backend/rag_engine.py` that computes 256-dimensional dense vectors using character 3-grams and subword token feature hashing, followed by L2 normalization. Because it computes vectors algorithmically without downloading multi-gigabyte neural network weights over the network, it works 100% offline with zero external network dependencies, ensuring the project will never crash during a viva or offline demo.

---

### CATEGORY 3: PROMPTING, TONE PRESETS & TEMPLATES

#### Q8: What are the 6 tone presets available in your system?
**Answer:**
1. **Professional:** Balanced, courteous, structured with clear bulleted responsibilities.
2. **Friendly / Warm:** Cordial, positive, emphasizing shared progress.
3. **Urgent / Action-Oriented:** Direct, highlighting upcoming deadlines and blocking risks.
4. **Executive / Concise:** Bottom-Line-Up-Front (BLUF), zero fluff, focusing on KPIs.
5. **Persuasive / Sales:** Focused on ROI, overcoming technical objections, and demo scheduling.
6. **Polite Re-engagement:** Low-pressure, considerate follow-up for unresponsive leads.

#### Q9: How do source citations work in your generated emails?
**Answer:** When the RAG engine queries Chroma, it returns the top matching chunks along with their source filename, chunk index, and cosine relevance score. The assistant attaches these citations to the response object, and the Streamlit UI displays them in an expandable citation drawer so users can verify the exact meeting transcript excerpt that informed each part of the draft.

#### Q10: How does the Template Library operate?
**Answer:** Templates are managed by `backend/template_library.py` and stored in `data/templates/default_templates.json`. Each template defines a category, description, subject template string with dynamic placeholders (e.g. `{meeting_title}`, `{date}`, `{client_name}`), and an ordered list of structural sections. Users can also define and save custom templates directly through the UI.

---

### CATEGORY 4: FASTAPI BACKEND & REST ARCHITECTURE

#### Q11: What are the key REST API endpoints exposed by your FastAPI server?
**Answer:**
- `GET /api/health`: Health status, indexed chunk statistics, student metadata.
- `POST /api/documents/upload`: Uploads and chunks raw text into Chroma.
- `GET /api/documents/list`: Lists indexed documents with chunk counts.
- `POST /api/documents/refresh`: Admin refresh workflow re-indexing sample meetings.
- `POST /api/drafts/generate`: Primary endpoint generating drafts with RAG and citations.
- `POST /api/suggestions/replies`: Returns smart next-step action chips.
- `GET /api/templates`: Returns email templates.
- `POST /api/export`: Formats draft into TXT, MD, HTML, EML, or JSON.
- `GET /api/history`: Returns generation history and usage analytics.

#### Q12: How is security / access control implemented?
**Answer:** In `backend/main.py`, the administrative re-indexing endpoint (`/api/documents/refresh`) uses FastAPI's `Depends(verify_admin_key)` dependency, validating an `X-Admin-Key` header against `settings.ADMIN_API_KEY`. Unauthorized attempts receive an immediate HTTP 401 Unauthorized response, fulfilling the Week 3 access control requirement.

#### Q13: What data validation is performed on API payloads?
**Answer:** We use **Pydantic V2** schemas in `backend/models.py`. Every incoming request and outgoing response is strictly typed and validated, preventing malformed payloads, injection of invalid tone types, or missing required fields.

---

### CATEGORY 5: FRONTEND, EXPORT & TESTING

#### Q14: How does the RFC 822 Outlook EML export work?
**Answer:** In `backend/export_service.py`, we construct an `EmailMessage` object conforming to the RFC 822 standard. We inject `Subject`, `To`, `From`, `Date`, and custom headers like `X-Mailer: Follow-up Reply Assistant (PRJ-042)`. When downloaded with the `.eml` extension, modern operating systems associate it with Microsoft Outlook, Apple Mail, or Mozilla Thunderbird, opening an editable compose window with one click!

#### Q15: How did you test the application across the 3-week milestone plan?
**Answer:** We built a 15-test automated pytest suite divided into 3 dedicated modules:
- `test_week1_kb.py`: Validates document parsing, metadata extraction, chunking overlap, and Chroma storage.
- `test_week2_retrieval.py`: Validates answer relevance, citation correctness, tone variation, and edge query handling.
- `test_week3_e2e.py`: Tests the complete FastAPI REST API, export module, access control, and audit history.
All 15 tests pass with a 100% success rate in under 2 seconds.

#### Q16: How is session history and analytics tracked?
**Answer:** `backend/history_manager.py` maintains an audit trail in `data/history.json`. Each entry records timestamp, recipient, subject, tone, word count, and citation count. The `/api/history/analytics` endpoint computes KPI metrics including total drafts generated, tone distribution, and average word count.
