import streamlit as st

# simple login (demo)
USER = "admin"
PASS = "1234"

st.title("🔐 Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if username == USER and password == PASS:
        st.session_state.logged_in = True
        st.success("Login successful")
        st.switch_page("app.py")
    else:
        st.error("Invalid credentials")