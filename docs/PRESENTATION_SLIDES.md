# 🎬 PRESENTATION SLIDES & 2-3 MINUTE DEMO VIDEO SCRIPT

## PROJECT CODE: PRJ-042 | FOLLOW-UP REPLY ASSISTANT
**Student:** SIVASURYA.B PSVPEC (Reg No: 411723205052)  
**Department:** Information Technology | **Domain:** Business | **Focus:** GenAI  

---

## 📽️ PART 1: TIMED 2-3 MINUTE VIDEO SCRIPT

> **Instructions for Recording:**  
> Use OBS Studio, Loom, or Windows Game Bar (`Win + G`) to record your screen and microphone. Keep the Streamlit UI open at `http://localhost:8501`.

```
================================================================================
TIMELINE & SPEAKER SCRIPT (TOTAL DURATION: 2 MIN 45 SEC)
================================================================================

[0:00 - 0:25] INTRO & STUDENT IDENTIFICATION
Speaker:
"Hello everyone and respected evaluators. My name is Sivasurya B, Register Number 
411723205052, from the Department of Information Technology at PSVPEC. 
Today, I am presenting my GenAI project: Project PRJ-042, the 'Follow-up Reply Assistant', 
built using FastAPI, LangChain, Streamlit, and Chroma Vector Database."

[0:25 - 0:55] PROBLEM STATEMENT & ARCHITECTURE
Speaker:
"In modern business, writing meeting recaps, action items, and sales follow-ups 
takes hours and often leads to dropped commitments. 
Our solution ingests raw meeting transcripts and customer call notes, chunks them 
into our Chroma Vector Database, and uses Retrieval-Augmented Generation to generate 
context-aware, professional email drafts with 6 distinct tone presets, citations, 
and next-step suggestions."

[0:55 - 1:40] LIVE DEMO: DRAFT GENERATOR & TONE PRESETS (SHOW SCREEN)
Speaker:
"Let's look at the live application. 
Here on the Draft Generator tab, I click on the quick demo button 'Acme Sales'. 
The discovery call notes are instantly loaded, showing 250 enterprise seats, budget, 
and SOC2 security concerns. 
I select the 'Persuasive / Sales' tone preset and click 'Generate Follow-up Draft'.
In seconds, the assistant generates a structured subject line, addresses Elena Rostova, 
outlines the ROI model, addresses the SOC2 compliance objection, and sets up Tuesday's demo!
Notice the smart reply chips at the top, like 'Attach Enterprise Pricing' and 
'Share Security Whitepaper'. 
Down below, the Citations expander reveals the exact source document and chunk from Chroma!"

[1:40 - 2:10] MULTI-FORMAT EXPORT & RFC 822 OUTLOOK EML
Speaker:
"Our project is fully send-ready. We provide multi-format exports: Plain Text, Markdown, 
Rendered HTML email, and Outlook EML format. 
When I click 'Outlook EML', it downloads a standard RFC 822 file that opens natively 
in Microsoft Outlook or Apple Mail with headers pre-filled!"

[2:10 - 2:35] KNOWLEDGE BASE, ADMIN REFRESH & TESTING
Speaker:
"In the Knowledge Base tab, users can upload new documents and test vector similarity search. 
We also implemented an Admin Refresh endpoint protected with an X-Admin-Key. 
In the History tab, every generation is logged with word counts and tone telemetry. 
Our complete automated pytest suite passes 15 out of 15 tests across Week 1, Week 2, 
and Week 3 requirements."

[2:35 - 2:45] CONCLUSION
Speaker:
"To conclude, PRJ-042 demonstrates a complete, reliable, production-ready GenAI assistant 
that bridges the gap between meeting discussions and business action. 
Thank you for your time!"
================================================================================
```

---

## 📊 PART 2: PRESENTATION SLIDES (PPT OUTLINE)

### Slide 1: Title Slide
- **Title:** Follow-up Reply Assistant (PRJ-042)
- **Subtitle:** GenAI-Powered Email Drafts & Action Item Extraction
- **Student Details:** SIVASURYA.B | Reg No: 411723205052
- **Department:** Information Technology, PSVPEC
- **Recommended Stack:** FastAPI + LangChain + Streamlit + Chroma

### Slide 2: Problem Statement & Motivation
- **The Challenge:** High latency in sending post-meeting recaps; dropped action items; tone mismatch; lack of audit tracking.
- **The Goal:** Build an automated GenAI assistant that converts meeting context into send-ready follow-up drafts in seconds.

### Slide 3: Decoupled System Architecture
- **Frontend Layer:** Streamlit executive web application with custom business styling.
- **REST API Layer:** FastAPI server providing `/api/drafts`, `/api/documents`, `/api/export`.
- **GenAI / RAG Pipeline:** LangChain chunker, Chroma persistent vector database, 6 tone presets, and context-aware intelligence engine.
- **Storage Layer:** Sample meetings repository, JSON template store, audit trail logger.

### Slide 4: Week 1 Implementation (Knowledge Base & Ingestion)
- Hierarchical document parsing (.txt, .md, .json, .csv).
- Metadata extraction: titles, meeting dates, attendees.
- Recursive character text chunking (400 chars, 80 overlap).
- Vector indexing in Chroma DB.

### Slide 5: Week 2 Implementation (Retrieval, Tones & Citations)
- Semantic vector similarity search with cosine relevance scoring.
- 6 Professional Tone Presets: Professional, Friendly, Urgent, Executive, Sales, Re-engagement.
- Automatic citation attribution linking drafts to specific chunks.
- Admin refresh workflow secured by `X-Admin-Key`.

### Slide 6: Week 3 Implementation (UX, Export & Audit)
- Interactive live draft editor with editable subject and body.
- Smart reply suggestion action chips.
- 5 export formats: Plain Text, Markdown, HTML Email, RFC 822 Outlook `.eml`, and JSON.
- Session audit trail and tone usage analytics.

### Slide 7: Automated Testing & Validation (15/15 Passed)
- Week 1 tests: Document parser, chunking boundaries, Chroma storage.
- Week 2 tests: Retrieval relevance, tone style differentiation, edge cases.
- Week 3 tests: Full FastAPI REST endpoints, multi-format export, access control.
- 100% test pass rate with pytest in 1.53 seconds.

### Slide 8: Live Demonstration Highlights
- Acme Global Sales Discovery: Demo scheduling and SOC2 compliance handling.
- Q3 Product Sync: Microservices migration recap and blocker escalation.
- Nexus Financial Onboarding: Webhook patch confirmation and revised timeline.

### Slide 9: Technology Stack & Design Decisions
- **FastAPI:** High-performance asynchronous REST API with auto-generated Swagger documentation.
- **Chroma:** Embeddable, persistent vector database requiring zero external cloud subscriptions.
- **Streamlit:** Rapid, responsive UI with stateful widgets and session management.
- **Deterministic Semantic Hashing:** Ensures 100% offline predictability during evaluations.

### Slide 10: Conclusion & Submission Deliverables
- GitHub Repository Structure & Progressive Commits.
- Complete documentation, academic report, and viva guide.
- Live deployment readiness (Streamlit Cloud & Render).
- **Marks Target:** 45 / 45 Marks.
