# 📸 SCREENSHOTS & DEMONSTRATION WALKTHROUGH GUIDE

## PROJECT CODE: PRJ-042 | FOLLOW-UP REPLY ASSISTANT
**Student:** SIVASURYA.B PSVPEC (Reg No: 411723205052)  

---

## 📌 OVERVIEW
This document outlines the visual structure, layout, and step-by-step verification points for capturing submission screenshots and conducting live demonstrations of the **Follow-up Reply Assistant**.

---

## 🖼️ SCREENSHOT 1: DRAFT GENERATOR & SMART REPLY CHIPS
- **Location:** Tab 1 — *📝 Draft Generator*
- **Action:** Click the quick demo button **"Acme Sales"**, select Tone **"Persuasive / Sales"**, and click **"Generate Follow-up Email Draft"**.
- **What to Capture:**
  - Sidebar showing Student Details: `SIVASURYA.B (411723205052) - PRJ-042`.
  - Left pane with Acme Global discovery call notes loaded.
  - Right pane showing generated Subject line: `Next Steps & Partnership Proposal | Elena Rostova & Sales Discovery Call - Acme Global Logistics`.
  - Smart Reply Suggestion chips: `💼 Attach Enterprise Pricing & ROI Model`, `🔒 Share Security Whitepaper & SOC2 Pack`.
  - Live interactive draft editor with formatted recap and action items.
  - Word count and reading time badges (`~170 words | ~57s read`).

---

## 🖼️ SCREENSHOT 2: KNOWLEDGE BASE CITATIONS & RAG EXCERPTS
- **Location:** Tab 1 — *🔍 Knowledge Base Citations Accordion*
- **Action:** Expand the citations accordion below the generated draft.
- **What to Capture:**
  - Citation badges showing `📄 Source: sales_discovery_acme.txt (Chunk #0) | Relevance Score: 0.20`.
  - Snippet excerpt highlighting discussion of 250 enterprise seats, $120,000 budget, and SOC2 Type II requirements.
  - Evidence of RAG grounding.

---

## 🖼️ SCREENSHOT 3: MULTI-FORMAT EXPORT & SEND-READY OUTPUT
- **Location:** Tab 1 — *📥 Export & Send-Ready Output*
- **Action:** Observe the 5 export download buttons and click **"📧 Outlook EML"** or **"🌐 HTML Email"**.
- **What to Capture:**
  - The 5 format buttons: `Plain Text`, `Markdown`, `HTML Email`, `Outlook EML`, `JSON`.
  - Downloaded `.eml` file ready to open in Microsoft Outlook or Apple Mail.
  - Success alert: *"🎉 Follow-up email marked ready for dispatch!"*.

---

## 🖼️ SCREENSHOT 4: KNOWLEDGE BASE & CHROMA VECTOR STORE
- **Location:** Tab 2 — *📚 Knowledge Base & Ingestion*
- **Action:** View the indexed documents table and test a semantic vector search for *"ERP legacy migration"*.
- **What to Capture:**
  - Document upload widget (.txt, .md, .json, .csv).
  - Semantic vector search results showing matching chunk and similarity score.
  - Table of indexed documents: `sales_discovery_acme.txt`, `q3_product_sync.txt`, `client_status_onboarding.txt`, `enterprise_renewal_lead.txt` with chunk counts and attendee metadata.

---

## 🖼️ SCREENSHOT 5: TEMPLATE LIBRARY & 6 TONE PRESETS
- **Location:** Tab 3 — *📑 Template Library & Tones*
- **Action:** Expand different tone profiles and pre-built templates.
- **What to Capture:**
  - The 6 tone presets: Professional, Friendly/Warm, Urgent/Action-Oriented, Executive/Concise, Persuasive/Sales, Polite Re-engagement.
  - Built-in business templates list (Post-Meeting Minutes, Sales Discovery, Gentle Nudge, etc.).
  - Custom template creation form.

---

## 🖼️ SCREENSHOT 6: AUDIT HISTORY & ANALYTICS
- **Location:** Tab 4 — *📜 History & Audit*
- **Action:** Open audit history tab after generating 2-3 drafts.
- **What to Capture:**
  - KPI metric cards: *Total Drafts Generated*, *Average Word Count*, *Indexed Knowledge Chunks*, *Top Tone Used*.
  - Audit trail table showing timestamped draft generation logs with word counts and recipient details.

---

## 🖼️ SCREENSHOT 7: FASTAPI SWAGGER API DOCUMENTATION
- **Location:** `http://127.0.0.1:8000/docs`
- **Action:** Open the interactive FastAPI Swagger UI in browser.
- **What to Capture:**
  - Project Title: `Follow-up Reply Assistant (PRJ-042)`.
  - Endpoints under `System`, `Knowledge Base`, `Draft Generation`, `Suggestions`, `Template Library`, `Export Module`, and `History & Audit`.
  - Executed `/api/health` returning `200 OK` with student registration details.

---

## 🖼️ SCREENSHOT 8: PYTEST AUTOMATED TEST SUITE EXECUTION
- **Location:** Terminal console
- **Action:** Run `pytest -v tests/`.
- **What to Capture:**
  - All 15 test cases passing across `test_week1_kb.py`, `test_week2_retrieval.py`, and `test_week3_e2e.py`.
  - Final green summary: `15 passed in 1.53s`.
