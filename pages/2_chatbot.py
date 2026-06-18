import streamlit as st
import os
import time
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from database import save_chat

st.set_page_config(page_title="MediChat AI", layout="wide", page_icon="🩺")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background-color: #f0f4f8 !important;
}
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2942 0%, #1a3a5c 100%) !important;
    color: white;
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stButton button {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    color: white !important;
    border-radius: 8px;
    width: 100%;
    margin-bottom: 6px;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,255,255,0.2) !important;
}

.chat-row {
    display: flex;
    gap: 12px;
    margin: 10px 0;
    align-items: flex-start;
}
.chat-row.user-row { flex-direction: row-reverse; }

.avatar {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0; font-weight: 600;
}
.avatar.user-avatar { background: #2196F3; color: white; }
.avatar.bot-avatar  { background: #0f2942; color: white; }

.bubble {
    max-width: 72%;
    padding: 12px 16px;
    border-radius: 18px;
    font-size: 14.5px;
    line-height: 1.65;
    word-break: break-word;
}
.user-bubble {
    background: #2196F3;
    color: white;
    border-bottom-right-radius: 4px;
}
.bot-bubble {
    background: #ffffff;
    color: #1a2a3a;
    border: 1px solid #dde3ea;
    border-bottom-left-radius: 4px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.source-badge {
    display: inline-block;
    background: #e8f4fd;
    color: #1565C0;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 12px;
    margin: 3px 4px;
    border: 1px solid #bbdefb;
    font-weight: 500;
}

.confidence-bar-wrapper {
    background: #e0e0e0; border-radius: 6px; height: 6px;
    width: 100%; margin: 6px 0 2px;
}
.confidence-bar {
    background: linear-gradient(90deg, #2196F3, #00BCD4);
    height: 6px; border-radius: 6px;
    transition: width 0.5s ease;
}

.typing-indicator {
    display: flex; gap: 5px; align-items: center;
    padding: 10px 16px;
    background: white;
    border: 1px solid #dde3ea;
    border-radius: 18px;
    width: fit-content;
}
.typing-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #90A4AE; animation: bounce 1.2s infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%,80%,100% { transform: translateY(0); } 40% { transform: translateY(-6px); } }

.welcome-card {
    background: linear-gradient(135deg, #0f2942 0%, #1565C0 100%);
    color: white;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
}
.welcome-card h2 { margin: 0 0 4px; font-size: 22px; font-weight: 600; }
.welcome-card p  { margin: 0; opacity: 0.85; font-size: 14px; }

.stTextInput > div > div > input {
    border-radius: 24px !important;
    border: 1.5px solid #cfd8dc !important;
    padding: 12px 20px !important;
    font-size: 15px !important;
    background: white !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    color: #1a2a3a !important;
}
.stTextInput > div > div > input:focus {
    border-color: #2196F3 !important;
    box-shadow: 0 0 0 3px rgba(33,150,243,0.12) !important;
}

div[data-testid="column"] .stButton button {
    border-radius: 24px !important;
    background: #2196F3 !important;
    color: white !important;
    border: none !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    height: 48px !important;
}
div[data-testid="column"] .stButton button:hover {
    background: #1565C0 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(33,150,243,0.3) !important;
}

.disclaimer {
    font-size: 12px; color: #90A4AE;
    text-align: center; margin-top: 8px;
}
.disclaimer span { color: #EF5350; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------
# HELPER: extract answer from retrieved context
# -----------------------------------------------
def extract_answer_from_context(question: str, context: str):
    if not context.strip():
        return "I couldn't find relevant information in the knowledge base. Please try rephrasing.", 40

    question_lower = question.lower()
    stop = {"what", "are", "is", "the", "a", "an", "how", "why", "when",
            "where", "who", "which", "can", "do", "does", "for", "of",
            "in", "to", "and", "or", "be", "was", "were", "been",
            "have", "has", "had", "with", "that", "this", "these", "those"}
    keywords = [w for w in question_lower.split() if w not in stop and len(w) > 2]

    import re
    sentences = re.split(r'(?<=[.!?])\s+', context)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]

    if not sentences:
        return context[:500].strip(), 55

    scored = []
    for sent in sentences:
        sent_lower = sent.lower()
        score = sum(1 for kw in keywords if kw in sent_lower)
        scored.append((score, sent))

    scored.sort(key=lambda x: x[0], reverse=True)

    top = [s for sc, s in scored[:5] if sc > 0]
    if not top:
        top = [s for _, s in scored[:2]]

    answer = " ".join(top[:3]).strip()
    if not answer:
        answer = sentences[0]

    max_score = scored[0][0] if scored else 0
    confidence = min(92, max(50, 50 + max_score * 8))

    return answer, int(confidence)


# -----------------------------------------------
# LOAD MODELS
# -----------------------------------------------
@st.cache_resource
def load_models():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = FAISS.load_local(
        "medical_vector_db", embeddings, allow_dangerous_deserialization=True
    )
    return vectorstore

vectorstore = load_models()


# -----------------------------------------------
# SESSION STATE
# -----------------------------------------------
for key, default in {
    "history": [],
    "query_count": 0,
    "total_response_time": 0.0,
    "selected_topic": None,
    "last_query": "",
    "input_value": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# -----------------------------------------------
# SIDEBAR
# -----------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 12px 0 20px;">
        <div style="font-size:32px;">🩺</div>
        <div style="font-size:18px; font-weight:600; margin-top:6px;">MediChat AI</div>
        <div style="font-size:12px; opacity:0.7; margin-top:2px;">Powered by RAG + FAISS</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**📁 Upload New Document**")
    uploaded_file = st.file_uploader("", type=["pdf", "txt"], label_visibility="collapsed")
    if uploaded_file:
        os.makedirs("medical_pdf", exist_ok=True)
        file_path = os.path.join("medical_pdf", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        st.success(f"✅ {uploaded_file.name} saved! Run ingest.py to update.")

    st.markdown("---")

    avg_time = (
        st.session_state.total_response_time / st.session_state.query_count
        if st.session_state.query_count > 0 else 0
    )
    st.markdown(f"""
    <div style="padding: 12px 0;">
        <div style="font-size:13px; font-weight:600; margin-bottom:10px; opacity:0.9;">Session Stats</div>
        <div style="display:flex; justify-content:space-between; font-size:13px; margin:6px 0;">
            <span style="opacity:0.7;">Queries</span>
            <span style="font-weight:600;">{st.session_state.query_count}</span>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:13px; margin:6px 0;">
            <span style="opacity:0.7;">Avg. Response</span>
            <span style="font-weight:600;">{avg_time:.1f}s</span>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:13px; margin:6px 0;">
            <span style="opacity:0.7;">Knowledge Docs</span>
            <span style="font-weight:600;">11</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🧹 Clear Conversation"):
        st.session_state.history = []
        st.session_state.query_count = 0
        st.session_state.total_response_time = 0.0
        st.session_state.last_query = ""
        st.session_state.input_value = ""
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px; opacity:0.6; text-align:center; line-height:1.6;">
        Topics covered:<br>
        Diabetes · Cancer · COVID-19<br>
        Hypertension · Asthma · Stroke<br>
        Malaria · Tuberculosis · Kidney<br>
        Liver Disease · Heart Disease
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------
# MAIN CONTENT
# -----------------------------------------------
st.markdown("""
<div class="welcome-card">
    <h2>🩺 Medical AI Assistant</h2>
    <p>Ask questions about symptoms, conditions, and treatments — grounded in your medical knowledge base.</p>
</div>
""", unsafe_allow_html=True)

QUICK_TOPICS = [
    ("🩸 Diabetes",      "What are the symptoms and treatment options for diabetes?"),
    ("❤️ Heart Disease", "What causes heart disease and how can it be prevented?"),
    ("🫁 Asthma",        "What triggers asthma and what are effective treatments?"),
    ("🧠 Stroke",        "What are the warning signs of a stroke?"),
    ("🦠 COVID-19",      "What are the symptoms and complications of COVID-19?"),
    ("💉 Hypertension",  "How is high blood pressure managed and treated?"),
    ("🩻 Cancer",        "What are early warning signs of cancer?"),
    ("🦟 Malaria",       "What are the symptoms and prevention of malaria?"),
]

st.markdown("<p style='font-size:13px; color:#607D8B; margin-bottom:4px;'>Quick Questions</p>",
            unsafe_allow_html=True)
cols = st.columns(4)
for i, (label, query_text) in enumerate(QUICK_TOPICS):
    with cols[i % 4]:
        if st.button(label, key=f"topic_{i}", use_container_width=True):
            st.session_state.selected_topic = query_text
            st.session_state.last_query = ""

st.markdown("<hr style='margin: 16px 0; border-color:#dde3ea;'>", unsafe_allow_html=True)

# ── Chat history ──────────────────────────────────
if st.session_state.history:
    for item in st.session_state.history:
        q          = item["question"]
        a          = item["answer"]
        sources    = item.get("sources", [])
        confidence = item.get("confidence", 75)
        resp_time  = item.get("response_time", 0)

        st.markdown(f"""
        <div class="chat-row user-row">
            <div class="avatar user-avatar">You</div>
            <div class="bubble user-bubble">{q}</div>
        </div>
        """, unsafe_allow_html=True)

        source_badges = "".join(
            f'<span class="source-badge">📄 {s}</span>' for s in sources
        )
        bar_w = min(confidence, 100)

        st.markdown(f"""
        <div class="chat-row">
            <div class="avatar bot-avatar">AI</div>
            <div style="max-width:72%;">
                <div class="bubble bot-bubble">{a}</div>
                <div style="margin-top:8px; padding: 0 4px;">
                    <div style="font-size:11px; color:#90A4AE; margin-bottom:4px;">
                        Confidence &nbsp;
                        <strong style="color:#1565C0;">{confidence}%</strong>
                        &nbsp;·&nbsp; {resp_time:.1f}s
                    </div>
                    <div class="confidence-bar-wrapper">
                        <div class="confidence-bar" style="width:{bar_w}%;"></div>
                    </div>
                    {f'<div style="margin-top:6px;">{source_badges}</div>' if sources else ''}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align:center; padding: 40px 20px; color: #90A4AE;">
        <div style="font-size:48px; margin-bottom:12px;">💬</div>
        <div style="font-size:16px; font-weight:500; color:#607D8B;">Start a conversation</div>
        <div style="font-size:13px; margin-top:4px;">Ask a medical question or pick a topic above</div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------
# INPUT ROW
# -----------------------------------------------
st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
col_input, col_send = st.columns([5, 1])

# Handle topic pill prefill
if st.session_state.selected_topic:
    st.session_state.input_value = st.session_state.selected_topic
    st.session_state.selected_topic = None

with col_input:
    query = st.text_input(
        "",
        value=st.session_state.input_value,
        placeholder="Ask a medical question…",
        label_visibility="collapsed",
        key="chat_input"
    )

with col_send:
    send = st.button("Send ↗", use_container_width=True)

st.markdown("""
<div class="disclaimer">
    <span>⚠ Not medical advice.</span> Always consult a qualified healthcare professional.
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------
# PROCESS QUERY — no duplicates, clears input
# -----------------------------------------------
if send and query.strip():
    if query.strip() != st.session_state["last_query"]:
        st.session_state["last_query"]  = query.strip()
        st.session_state["input_value"] = ""   # clears the input box

        with st.spinner(""):
            typing_ph = st.empty()
            typing_ph.markdown("""
            <div class="chat-row" style="margin-top:8px;">
                <div class="avatar bot-avatar">AI</div>
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            t0      = time.time()
            docs    = vectorstore.similarity_search(query, k=5)
            context = "\n".join([doc.page_content for doc in docs])

            sources = list({
                os.path.basename(doc.metadata.get("source", ""))
                  .replace(".txt", "").replace("_", " ").title()
                for doc in docs if doc.metadata.get("source")
            })

            answer, confidence = extract_answer_from_context(query, context)
            elapsed = time.time() - t0
            typing_ph.empty()

        save_chat(query, answer)
        st.session_state.history.append({
            "question":      query,
            "answer":        answer,
            "sources":       sources[:3],
            "confidence":    confidence,
            "response_time": elapsed,
        })
        st.session_state.query_count         += 1
        st.session_state.total_response_time += elapsed
        st.rerun()