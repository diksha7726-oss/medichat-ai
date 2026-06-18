import streamlit as st
from database import get_history

st.set_page_config(page_title="Chat History", layout="wide", page_icon="📜")

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

.hist-card {
    background: white; border-radius: 12px;
    border: 1px solid #e8edf2;
    padding: 16px 20px; margin-bottom: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.hist-card .q-label {
    font-size: 12px; color: #2196F3; font-weight: 600;
    text-transform: uppercase; letter-spacing: .5px; margin-bottom: 4px;
}
.hist-card .q-text { font-size: 15px; font-weight: 500; color: #0f2942; margin-bottom: 10px; }
.hist-card .a-label {
    font-size: 12px; color: #43A047; font-weight: 600;
    text-transform: uppercase; letter-spacing: .5px; margin-bottom: 4px;
}
.hist-card .a-text { font-size: 13.5px; color: #37474F; line-height: 1.6; }
.hist-num {
    display: inline-block;
    background: #e8f4fd; color: #1565C0;
    border-radius: 6px; padding: 2px 9px;
    font-size: 12px; font-weight: 600; margin-right: 8px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: linear-gradient(135deg, #0f2942 0%, #1565C0 100%);
     border-radius: 16px; padding: 22px 28px; margin-bottom: 24px; color: white;">
    <h2 style="margin:0 0 4px; font-size:22px; font-weight:600;">📜 Chat History</h2>
    <p style="margin:0; opacity:.8; font-size:14px;">All previous conversations from the database</p>
</div>
""", unsafe_allow_html=True)

# DB history
db_history = get_history()
session_history = st.session_state.get("history", [])

col_a, col_b = st.columns([3, 1])
with col_b:
    if st.button("🧹 Clear Session History"):
        st.session_state.history = []
        st.success("Session history cleared!")
        st.rerun()

if not db_history:
    st.markdown("""
    <div style="text-align:center; padding:60px 20px; color:#90A4AE;">
        <div style="font-size:48px; margin-bottom:12px;">📭</div>
        <div style="font-size:16px; font-weight:500; color:#607D8B;">No history yet</div>
        <div style="font-size:13px; margin-top:4px;">Start a conversation in the Chatbot page</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"<p style='color:#607D8B; font-size:13px; margin-bottom:16px;'>{len(db_history)} conversation(s) found</p>", unsafe_allow_html=True)
    for i, (q, a) in enumerate(reversed(db_history), 1):
        st.markdown(f"""
        <div class="hist-card">
            <div><span class="hist-num">#{i}</span></div>
            <div class="q-label">Question</div>
            <div class="q-text">{q}</div>
            <div class="a-label">Answer</div>
            <div class="a-text">{a}</div>
        </div>
        """, unsafe_allow_html=True)
