import streamlit as st

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Medical AI System",
    page_icon="🧠",
    layout="wide"
)

# -------------------------------
# SESSION STATE
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -------------------------------
# LOGIN CHECK
# -------------------------------
if not st.session_state.logged_in:
    st.title("🔐 Login Required")
    st.warning("Please login to access the Medical AI System")

    st.info("👉 Go to the sidebar and click '0_Login' to login")

    st.stop()

# -------------------------------
# MAIN APP
# -------------------------------
col1, col2 = st.columns([1, 5])

with col1:
    st.image("logo.png", width=80)

with col2:
    st.title("🧠 Medical AI System")

st.markdown("""
## Welcome 👋

Use the sidebar to navigate:

- 📊 Dashboard  
- 💬 Chatbot  
- 📜 History  
""")

# -------------------------------
# LOGOUT BUTTON
# -------------------------------
if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.success("Logged out successfully")
    st.rerun()