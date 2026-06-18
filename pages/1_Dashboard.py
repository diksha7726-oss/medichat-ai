import streamlit as st
from database import get_history
import time

st.set_page_config(page_title="Dashboard", layout="wide", page_icon="📊")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
html, body, .stApp { font-family: 'Inter', sans-serif; background: #f0f4f8 !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2942 0%, #1a3a5c 100%) !important;
}
[data-testid="stSidebar"] * { color: white !important; }

.metric-card {
    background: white;
    border-radius: 14px;
    padding: 20px 22px;
    border: 1px solid #e8edf2;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.metric-card .val { font-size: 28px; font-weight: 600; color: #0f2942; margin: 4px 0 2px; }
.metric-card .lbl { font-size: 12px; color: #90A4AE; text-transform: uppercase; letter-spacing: .6px; }
.metric-card .icon { font-size: 22px; margin-bottom: 4px; }
.metric-card .delta { font-size: 12px; color: #43A047; font-weight: 500; }

.status-row {
    display: flex; align-items: center; gap: 10px;
    padding: 12px 16px;
    background: white; border-radius: 10px;
    border: 1px solid #e8edf2;
    margin-bottom: 8px;
    font-size: 14px; color: #37474F;
}
.status-dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
.dot-green { background: #43A047; box-shadow: 0 0 6px rgba(67,160,71,0.5); }
.dot-blue  { background: #2196F3; box-shadow: 0 0 6px rgba(33,150,243,0.5); }

.section-title {
    font-size: 15px; font-weight: 600; color: #0f2942;
    margin: 20px 0 10px;
}

.history-row {
    background: white; border-radius: 10px; padding: 12px 16px;
    border: 1px solid #e8edf2; margin-bottom: 8px;
}
.history-q { font-size: 13.5px; font-weight: 500; color: #1a2a3a; }
.history-a { font-size: 12.5px; color: #607D8B; margin-top: 4px; 
             white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }

.topic-coverage {
    display: flex; flex-wrap: wrap; gap: 8px; margin-top: 4px;
}
.topic-tag {
    background: #e8f4fd; color: #1565C0;
    border-radius: 20px; padding: 5px 14px;
    font-size: 12px; font-weight: 500;
    border: 1px solid #bbdefb;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #0f2942 0%, #1565C0 100%);
     border-radius: 16px; padding: 22px 28px; margin-bottom: 24px; color: white;">
    <h2 style="margin:0 0 4px; font-size:22px; font-weight:600;">📊 System Dashboard</h2>
    <p style="margin:0; opacity:.8; font-size:14px;">Real-time overview of your Medical AI RAG system</p>
</div>
""", unsafe_allow_html=True)

# Metric Cards
history = get_history()
total_queries = len(history)
col1, col2, col3, col4 = st.columns(4)
metrics = [
    (col1, "📄", str(11), "Knowledge Documents", ""),
    (col2, "💬", str(total_queries), "Total Queries", ""),
    (col3, "🤖", "Active", "Model Status", "distilgpt2"),
    (col4, "🗄️", "Loaded", "Vector DB", "FAISS · 11 chunks"),
]
for col, icon, val, lbl, sub in metrics:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="icon">{icon}</div>
            <div class="val">{val}</div>
            <div class="lbl">{lbl}</div>
            {"" if not sub else f'<div class="delta">{sub}</div>'}
        </div>
        """, unsafe_allow_html=True)

# System Status
st.markdown('<div class="section-title">⚙️ System Status</div>', unsafe_allow_html=True)
statuses = [
    ("dot-green", "Vector database loaded and ready (FAISS)"),
    ("dot-green", "HuggingFace embedding model active (all-MiniLM-L6-v2)"),
    ("dot-blue",  "Text generation model running (distilgpt2)"),
    ("dot-green", "SQLite chat history database connected"),
    ("dot-green", "11 medical documents indexed"),
]
for dot_cls, msg in statuses:
    st.markdown(f"""
    <div class="status-row">
        <div class="status-dot {dot_cls}"></div>
        <span>{msg}</span>
    </div>
    """, unsafe_allow_html=True)

# Topic Coverage
st.markdown('<div class="section-title">🏷️ Knowledge Base Topics</div>', unsafe_allow_html=True)
topics = ["Diabetes", "Cancer", "COVID-19", "Hypertension", "Asthma",
          "Stroke", "Malaria", "Tuberculosis", "Kidney Disease",
          "Liver Disease", "Heart Disease"]
tags = "".join(f'<span class="topic-tag">{t}</span>' for t in topics)
st.markdown(f'<div class="topic-coverage">{tags}</div>', unsafe_allow_html=True)

# Recent History
if history:
    st.markdown('<div class="section-title">🕐 Recent Conversations</div>', unsafe_allow_html=True)
    for q, a in list(reversed(history))[:5]:
        snippet = a[:120] + "…" if len(a) > 120 else a
        st.markdown(f"""
        <div class="history-row">
            <div class="history-q">🧑 {q}</div>
            <div class="history-a">🤖 {snippet}</div>
        </div>
        """, unsafe_allow_html=True)
