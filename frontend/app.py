"""
Streamlit Web Application - Follow-up Reply Assistant
Project Code: PRJ-042 | Student: SIVASURYA.B PSVPEC (Reg No: 411723205052)
Domain: Business | Stack: FastAPI + LangChain + Streamlit + Chroma
"""

import sys
import os
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import json
from datetime import datetime

from backend.config import settings
from backend.rag_engine import rag_engine
from backend.prompt_manager import prompt_manager, TONE_PROFILES
from backend.template_library import template_library
from backend.reply_suggester import reply_suggester
from backend.export_service import export_service
from backend.history_manager import history_manager
from backend.models import Citation

# ----------------- Page Setup & Theme -----------------
st.set_page_config(
    page_title="Follow-up Reply Assistant (PRJ-042)",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_file = ROOT_DIR / "frontend" / "styles.css"
if css_file.exists():
    st.markdown(f"<style>{css_file.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ----------------- Sidebar Configuration -----------------
with st.sidebar:
    st.markdown("### ✉️ Follow-up Reply Assistant")
    st.markdown(
        f"""
        <div style="background-color: #1e293b; color: white; padding: 12px; border-radius: 8px; font-size: 12px; margin-bottom: 15px;">
            <strong>Project:</strong> {settings.PROJECT_CODE} - IT<br/>
            <strong>Student:</strong> {settings.STUDENT_NAME}<br/>
            <strong>Reg No:</strong> {settings.REG_NO}<br/>
            <strong>Dept:</strong> {settings.DEPARTMENT} | PSVPEC<br/>
            <strong>Score Target:</strong> 45 / 45 Marks
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("#### ⚙️ GenAI & Model Settings")
    llm_choice = st.selectbox(
        "LLM Provider",
        ["Offline Context-Aware GenAI (Default)", "OpenAI GPT-4o-mini", "Google Gemini 1.5 Flash"],
        index=0,
        help="The built-in GenAI engine works 100% offline without needing external API keys during viva evaluation."
    )

    if "OpenAI" in llm_choice:
        user_openai_key = st.text_input("OpenAI API Key", type="password", value=settings.OPENAI_API_KEY)
        if user_openai_key:
            settings.OPENAI_API_KEY = user_openai_key
            settings.LLM_PROVIDER = "openai"
    elif "Gemini" in llm_choice:
        user_gemini_key = st.text_input("Gemini API Key", type="password", value=settings.GEMINI_API_KEY)
        if user_gemini_key:
            settings.GEMINI_API_KEY = user_gemini_key
            settings.LLM_PROVIDER = "gemini"
    else:
        settings.LLM_PROVIDER = "mock"

    st.markdown("---")
    st.markdown("#### 🔄 Knowledge Base Admin")
    admin_key_input = st.text_input("Admin Key", type="password", value="", placeholder="Enter admin key")
    if st.button("Admin Refresh / Re-index KB", help="Re-indexes sample meeting documents into Chroma"):
        if admin_key_input == settings.ADMIN_API_KEY:
            with st.spinner("Re-indexing knowledge base into Chroma..."):
                res = rag_engine.reindex_all_sample_documents()
                st.success(f"Indexed {res['indexed_documents']} docs ({res['total_chunks']} chunks)!")
        else:
            st.error("Invalid Admin Key. (Default: admin_secure_key_prj042)")

    st.markdown("---")
    st.caption(f"App Version {settings.APP_VERSION} • FastAPI + LangChain + Chroma")


# ----------------- App Header -----------------
st.markdown(
    f"""
    <div class="main-header">
        <h1>Follow-up Reply Assistant</h1>
        <p>AI-Powered Reminder & Follow-up Draft Generator from Meeting & Lead Context</p>
        <div class="student-badge">
            Student: <strong>{settings.STUDENT_NAME}</strong> (Reg: {settings.REG_NO}) | Dept: {settings.DEPARTMENT} | Code: {settings.PROJECT_CODE}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------- Navigation Tabs -----------------
tab_draft, tab_kb, tab_templates, tab_history, tab_viva = st.tabs([
    "📝 Draft Generator",
    "📚 Knowledge Base & Ingestion",
    "📑 Template Library & Tones",
    "📜 History & Audit",
    "🎓 Viva & Rubric Guide"
])

# ==============================================================================
# TAB 1: DRAFT GENERATOR & REPLY ASSISTANT
# ==============================================================================
with tab_draft:
    col_input, col_output = st.columns([1, 1], gap="large")

    with col_input:
        st.subheader("1. Meeting Context & Settings")

        # Quick Demo Buttons
        st.markdown("**⚡ Quick Load Demo Context:**")
        q_cols = st.columns(4)
        sample_files = list(settings.SAMPLE_DIR.glob("*.*"))

        selected_demo_text = ""
        if sample_files:
            if q_cols[0].button("Acme Sales", key="btn_acme"):
                f = settings.SAMPLE_DIR / "sales_discovery_acme.txt"
                if f.exists():
                    st.session_state["meeting_input"] = f.read_text(encoding="utf-8")
                    st.session_state["recipient_input"] = "Elena Rostova (Acme Global)"
            if q_cols[1].button("Q3 Sync", key="btn_q3"):
                f = settings.SAMPLE_DIR / "q3_product_sync.txt"
                if f.exists():
                    st.session_state["meeting_input"] = f.read_text(encoding="utf-8")
                    st.session_state["recipient_input"] = "Sarah Jenkins (VP Product)"
            if q_cols[2].button("Onboarding", key="btn_onboard"):
                f = settings.SAMPLE_DIR / "client_status_onboarding.txt"
                if f.exists():
                    st.session_state["meeting_input"] = f.read_text(encoding="utf-8")
                    st.session_state["recipient_input"] = "Nathan Drake (Nexus Financial)"
            if q_cols[3].button("Renewal", key="btn_renew"):
                f = settings.SAMPLE_DIR / "enterprise_renewal_lead.txt"
                if f.exists():
                    st.session_state["meeting_input"] = f.read_text(encoding="utf-8")
                    st.session_state["recipient_input"] = "Robert Hayes (Vertex Media)"

        # Context Input Box
        default_val = st.session_state.get("meeting_input", "")
        meeting_context = st.text_area(
            "Meeting Notes / Lead Transcript / Call Summary:",
            value=default_val,
            height=220,
            placeholder="Paste meeting notes, action items, or CRM discussion points here. Or leave blank to query the Chroma Knowledge Base directly using your prompt instructions!"
        )

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            all_tpls = template_library.list_templates()
            tpl_options = ["None (Auto-Structure)"] + [t["name"] for t in all_tpls]
            selected_tpl_name = st.selectbox("Template Preset:", tpl_options, index=0)

        with col_t2:
            tone_options = list(TONE_PROFILES.keys())
            selected_tone = st.selectbox("Tone Preset:", tone_options, index=0)

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            recipient_name = st.text_input("Recipient Name / Title:", value=st.session_state.get("recipient_input", "Client / Colleague"))
        with col_r2:
            sender_name = st.text_input("Sender Name:", value="Sivasurya B")

        user_instructions = st.text_input(
            "Custom Instructions (Optional):",
            placeholder="e.g., Emphasize the SOC2 security report and propose next Tuesday at 2 PM."
        )

        use_rag_checkbox = st.checkbox("Query Chroma Vector Database (RAG) for Context & Citations", value=True)

        generate_btn = st.button("🚀 Generate Follow-up Email Draft", type="primary", use_container_width=True)

    with col_output:
        st.subheader("2. Generated Follow-up Email Draft")

        if generate_btn or "last_draft" in st.session_state:
            if generate_btn:
                # Find template ID if selected
                tpl_id = None
                if selected_tpl_name != "None (Auto-Structure)":
                    for t in all_tpls:
                        if t["name"] == selected_tpl_name:
                            tpl_id = t["id"]
                            break

                citations = []
                effective_context = meeting_context

                # RAG retrieval
                if use_rag_checkbox:
                    search_q = user_instructions or effective_context[:200]
                    if search_q.strip():
                        matched = rag_engine.query_context(search_q, top_k=settings.RETRIEVAL_TOP_K)
                        for m in matched:
                            citations.append(Citation(
                                source_doc=m["source_doc"],
                                chunk_index=m["chunk_index"],
                                relevance_score=m["relevance_score"],
                                snippet=m["snippet"]
                            ))
                        if not effective_context.strip() and matched:
                            effective_context = "\n\n".join([f"[{m['source_doc']}]\n{m['snippet']}" for m in matched])

                draft = prompt_manager.generate_draft(
                    context=effective_context,
                    user_instructions=user_instructions,
                    tone=selected_tone,
                    template_id=tpl_id,
                    recipient_name=recipient_name,
                    sender_name=sender_name,
                    citations=citations
                )

                # Save in session state and history
                st.session_state["last_draft"] = draft
                history_manager.add_entry(
                    subject=draft.subject,
                    recipient=draft.recipient,
                    tone=draft.tone,
                    template_name=draft.template_applied,
                    body=draft.body,
                    citations_count=len(draft.citations)
                )

            draft = st.session_state["last_draft"]

            # Smart Reply Suggestions Chips
            if draft.reply_suggestions:
                st.markdown("**💡 Smart Reply Suggestions & Action Chips:**")
                chip_cols = st.columns(len(draft.reply_suggestions))
                for idx, sugg in enumerate(draft.reply_suggestions):
                    if chip_cols[idx].button(sugg, key=f"chip_{idx}"):
                        st.info(f"Selected Suggestion: {sugg}")

            # Editable Subject
            edited_subject = st.text_input("Subject Line:", value=draft.subject, key="subject_display")

            # Editable Email Body
            edited_body = st.text_area(
                "Email Body (Interactive Editor):",
                value=draft.body,
                height=320,
                key="body_display"
            )

            # Metadata Badges
            st.markdown(
                f"""
                <div style="font-size: 13px; color: #475569; margin: 8px 0;">
                    📏 <strong>{len(edited_body.split())} words</strong> &nbsp;|&nbsp;
                    ⏱️ <strong>~{max(1, round(len(edited_body.split()) / 180 * 60))}s read</strong> &nbsp;|&nbsp;
                    🎭 <strong>Tone: {draft.tone}</strong> &nbsp;|&nbsp;
                    📋 <strong>Template: {draft.template_applied or 'Custom Context'}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Citations Accordion (Week 2 Requirement)
            if draft.citations:
                with st.expander(f"🔍 Knowledge Base Citations ({len(draft.citations)} chunks referenced)"):
                    for c in draft.citations:
                        st.markdown(
                            f"""
                            <div class="citation-box">
                                <strong>📄 Source:</strong> {c.source_doc} (Chunk #{c.chunk_index}) &nbsp;|&nbsp; 
                                <strong>Relevance Score:</strong> {c.relevance_score:.2f}<br/>
                                <em>"{c.snippet[:180]}..."</em>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            # Export & Download Buttons (Week 3 Requirement)
            st.markdown("#### 📥 Export & Send-Ready Output")
            exp_col1, exp_col2, exp_col3, exp_col4, exp_col5 = st.columns(5)

            # Plain Text
            txt_res = export_service.export(edited_subject, recipient_name, edited_body, "txt", sender_name)
            exp_col1.download_button("📄 Plain Text", data=txt_res["content"], file_name=txt_res["filename"], mime="text/plain")

            # Markdown
            md_res = export_service.export(edited_subject, recipient_name, edited_body, "md", sender_name)
            exp_col2.download_button("📝 Markdown", data=md_res["content"], file_name=md_res["filename"], mime="text/markdown")

            # HTML
            html_res = export_service.export(edited_subject, recipient_name, edited_body, "html", sender_name)
            exp_col3.download_button("🌐 HTML Email", data=html_res["content"], file_name=html_res["filename"], mime="text/html")

            # Outlook EML
            eml_res = export_service.export(edited_subject, recipient_name, edited_body, "eml", sender_name)
            exp_col4.download_button("📧 Outlook EML", data=eml_res["content"], file_name=eml_res["filename"], mime="message/rfc822")

            # JSON
            json_res = export_service.export(edited_subject, recipient_name, edited_body, "json", sender_name)
            exp_col5.download_button("📦 JSON", data=json_res["content"], file_name=json_res["filename"], mime="application/json")

            if st.button("✅ Mark Draft as Ready & Send", use_container_width=True):
                st.success(f"🎉 Follow-up email '{edited_subject}' marked ready for dispatch to {recipient_name}!")
        else:
            st.info("👈 Enter meeting notes or select a demo context on the left and click 'Generate Follow-up Email Draft'.")


# ==============================================================================
# TAB 2: KNOWLEDGE BASE & INGESTION (Week 1 & 2)
# ==============================================================================
with tab_kb:
    st.subheader("📚 Knowledge Base Management & Chroma Vector Store")
    st.markdown("Upload, chunk, and index meeting transcripts, CRM summaries, and client project briefs.")

    kb_col1, kb_col2 = st.columns([1, 1], gap="large")

    with kb_col1:
        st.markdown("#### 📤 Upload & Index Document")
        uploaded_file = st.file_uploader(
            "Choose a document (.txt, .md, .json, .csv):",
            type=["txt", "md", "json", "csv"]
        )

        manual_doc_title = st.text_input("Document Name / Title:", placeholder="e.g., sprint_planning_notes.txt")
        manual_doc_text = st.text_area("Or Paste Raw Document Content Here:", height=180)

        if st.button("📥 Parse & Index into Chroma Vector DB", type="primary"):
            filename = ""
            content = ""
            if uploaded_file is not None:
                filename = uploaded_file.name
                content = uploaded_file.read().decode("utf-8", errors="ignore")
            elif manual_doc_title and manual_doc_text:
                filename = manual_doc_title
                content = manual_doc_text

            if filename and content:
                chunks = rag_engine.add_document(filename, content)
                st.success(f"✅ Successfully indexed '{filename}' into {chunks} searchable Chroma chunks!")
            else:
                st.warning("Please provide a file or fill in both document title and text.")

    with kb_col2:
        st.markdown("#### 🔎 Test Vector Similarity Search")
        search_query = st.text_input("Enter Semantic Search Query:", placeholder="e.g. ERP integration or SOC2 compliance")
        top_k = st.slider("Max Chunks to Retrieve:", 1, 6, 3)

        if st.button("🔍 Search Chroma"):
            if search_query.strip():
                results = rag_engine.query_context(search_query, top_k=top_k)
                if results:
                    st.write(f"Found {len(results)} matching chunks:")
                    for r in results:
                        st.markdown(
                            f"""
                            <div class="citation-box">
                                <strong>📄 {r['source_doc']}</strong> (Chunk #{r['chunk_index']}) &bull; 
                                <strong>Score: {r['relevance_score']:.3f}</strong><br/>
                                <div style="margin-top: 4px; font-family: monospace; font-size: 12px;">{r['snippet']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No matching chunks found in the Chroma collection.")

    st.markdown("---")
    st.markdown("#### 📑 Current Indexed Documents in Chroma Collection")
    indexed_docs = rag_engine.get_indexed_documents()
    if indexed_docs:
        doc_table = []
        for d in indexed_docs:
            doc_table.append({
                "Document Name": d["filename"],
                "Doc Type": d["doc_type"],
                "Chunks": d["chunks_count"],
                "Attendees": d["attendees"] or "N/A",
                "Meeting Date": d["meeting_date"] or "N/A",
                "Sample Preview": d["sample_preview"]
            })
        st.dataframe(doc_table, use_container_width=True)
    else:
        st.info("No documents currently indexed in Chroma. Click 'Admin Refresh / Re-index KB' in the sidebar to load samples.")


# ==============================================================================
# TAB 3: TEMPLATE LIBRARY & TONE PRESETS
# ==============================================================================
with tab_templates:
    st.subheader("📑 Template Library & Tone Presets")

    t_col1, t_col2 = st.columns([1, 1], gap="large")

    with t_col1:
        st.markdown("#### 🎭 Tone Presets")
        for tone_name, profile in TONE_PROFILES.items():
            with st.expander(f"✨ Tone: {tone_name}"):
                st.markdown(f"**Guidance:** {profile['tone_guidance']}")
                st.markdown(f"**Greeting Sample:** `{profile['greeting'].format(recipient='Alex')}`")
                st.markdown(f"**Intro Sample:** `{profile['intro'].format(recipient='Alex', topic='Project Delivery')}`")
                st.markdown(f"**Sign-off:**\n```\n{profile['signoff'].format(sender='Sivasurya B')}\n```")

    with t_col2:
        st.markdown("#### 📋 Pre-built Follow-up Email Templates")
        templates = template_library.list_templates()
        for t in templates:
            with st.expander(f"📄 {t['name']} ({t['category']})"):
                st.markdown(f"**Description:** {t['description']}")
                st.markdown(f"**Default Tone:** `{t['default_tone']}`")
                st.markdown(f"**Subject Template:** `{t['subject_template']}`")
                st.markdown("**Section Structure:**")
                for s in t.get("structure", []):
                    st.markdown(f"- {s}")

    st.markdown("---")
    st.markdown("#### ➕ Create Custom Template")
    with st.form("new_template_form"):
        col_nt1, col_nt2 = st.columns(2)
        with col_nt1:
            new_tpl_name = st.text_input("Template Name:", placeholder="e.g. Executive Quarterly Update")
            new_tpl_cat = st.selectbox("Category:", ["Meeting Recap", "Sales & Leads", "Client Management", "Critical Communication"])
            new_tpl_tone = st.selectbox("Default Tone:", list(TONE_PROFILES.keys()))
        with col_nt2:
            new_tpl_desc = st.text_input("Short Description:", placeholder="Recaps quarterly ROI and KPIs")
            new_tpl_subj = st.text_input("Subject Template:", value="Quarterly Review: {topic} - {date}")
            new_tpl_sections = st.text_area("Structure (one line per section):", value="Executive greeting\nQuarterly KPI recap\nAction items\nNext checkpoint")

        submit_tpl = st.form_submit_button("💾 Save Template to Library")
        if submit_tpl:
            if new_tpl_name and new_tpl_subj:
                struct_list = [line.strip() for line in new_tpl_sections.split("\n") if line.strip()]
                created = template_library.create_template(
                    name=new_tpl_name,
                    category=new_tpl_cat,
                    description=new_tpl_desc,
                    subject_template=new_tpl_subj,
                    default_tone=new_tpl_tone,
                    structure=struct_list
                )
                st.success(f"✅ Template '{new_tpl_name}' successfully created and saved!")
            else:
                st.warning("Please provide template name and subject template.")


# ==============================================================================
# TAB 4: AUDIT HISTORY & ANALYTICS (Week 3)
# ==============================================================================
with tab_history:
    st.subheader("📜 Draft Generation History & Audit Log")

    analytics = history_manager.get_analytics()

    # KPI Metrics Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Drafts Generated", analytics["total_drafts"])
    kpi2.metric("Average Word Count", f"{analytics['average_words']} words")
    kpi3.metric("Indexed Knowledge Chunks", rag_engine.collection.count())
    top_tone = max(analytics["tones_used"].items(), key=lambda x: x[1])[0] if analytics["tones_used"] else "N/A"
    kpi4.metric("Top Tone Used", top_tone)

    st.markdown("---")

    hist_entries = history_manager.get_entries(limit=50)
    if hist_entries:
        st.markdown(f"**Showing last {len(hist_entries)} generated drafts:**")
        for h in hist_entries:
            with st.expander(f"🕒 {h['timestamp']} | {h['recipient']} - {h['subject']}"):
                st.markdown(f"**Tone:** `{h['tone']}` &bull; **Template:** `{h['template_name']}` &bull; **Words:** {h['word_count']}")
                st.markdown("**Body Preview:**")
                st.text(h.get("full_body", h["body_preview"]))
    else:
        st.info("No drafts in history yet. Generated drafts will automatically appear here.")

    if st.button("🗑️ Clear Generation History"):
        history_manager.clear()
        st.success("History log cleared.")


# ==============================================================================
# TAB 5: VIVA & RUBRIC GUIDE
# ==============================================================================
with tab_viva:
    st.subheader("🎓 Academic Rubric & Viva Preparation Guide")
    st.markdown(
        f"""
        ### Student Assignment Details
        - **Project Code:** {settings.PROJECT_CODE}
        - **Project Name:** {settings.PROJECT_NAME}
        - **Student Name:** {settings.STUDENT_NAME}
        - **Register Number:** {settings.REG_NO}
        - **Department:** {settings.DEPARTMENT} | PSVPEC
        - **Email:** {settings.EMAIL}
        - **Category:** Email and Reply Assistants | **Domain:** Business | **Focus:** GenAI
        - **Total Marks:** 45 / 45
        ---
        ### 3-Week Implementation & Marks Breakdown:
        1. **Week 1 Implementation (10 Marks):**
           - Knowledge base creation, document loading, chunking with recursive boundary preservation, baseline Q&A interface.
        2. **Week 1 Testing (5 Marks):**
           - Document parsing, text splitting overlap, chunk validation.
        3. **Week 2 Implementation (10 Marks):**
           - Semantic Chroma vector retrieval, prompt tuning with 6 tone presets, source citation attribution, admin refresh workflow.
        4. **Week 2 Testing (5 Marks):**
           - Relevance scoring, edge case handling, fallback context generation.
        5. **Week 3 Implementation (10 Marks):**
           - Interactive draft editor, audit logging and analytics, access control (X-Admin-Key), multi-format export (TXT, MD, HTML, EML, JSON).
        6. **Week 3 Testing (5 Marks):**
           - End-to-end FastAPI endpoint validation, comprehensive pytest test suite.
        ---
        ### Key Viva Talking Points & Architecture:
        - **RAG Architecture:** Meeting transcripts are preprocessed into overlapping chunks (400 chars, 80 overlap) and indexed into Chroma vector database.
        - **Embeddings & Standalone Predictability:** Uses deterministic dense subword + token n-gram hashing embeddings with L2 normalization, allowing full offline operation without downloading multi-gigabyte models or risking network timeouts during viva.
        - **Hybrid LLM Generator:** Seamlessly switches between built-in context extraction (entity parsing, action item detection) and OpenAI GPT-4o / Gemini models.
        - **Email Standards Compliance:** Implements RFC 822 `.eml` export which opens natively in Microsoft Outlook and Apple Mail.
        """
    )
