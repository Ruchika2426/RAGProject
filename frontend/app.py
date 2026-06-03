import os
import streamlit as st
import requests

# Constants
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000/chat")

st.set_page_config(page_title="HDFC Mutual Fund Assistant", page_icon="📈")

st.title("HDFC Mutual Fund FAQ Assistant")
st.markdown("Welcome! I can answer factual questions about HDFC mutual funds based on official documentation.")

# Prominent Disclaimer
st.warning("**Disclaimer:** Facts-only. No investment advice. Please consult a SEBI registered advisor for investment recommendations.")

st.markdown("### Example Questions:")

example_questions = [
    "What is the exit load for HDFC Small Cap Fund?",
    "What is the AUM of HDFC Liquid Fund?",
    "Who are the fund managers for HDFC Flexi Cap?"
]

# Use columns for example buttons to make UI look cleaner
cols = st.columns(3)
for i, q in enumerate(example_questions):
    if cols[i].button(q):
        st.session_state.query = q

if "query" not in st.session_state:
    st.session_state.query = ""

user_query = st.text_input("Ask a question about HDFC mutual funds:", value=st.session_state.query)

if st.button("Submit") or user_query != st.session_state.query:
    # Handle enter key submission properly by checking if text changed and button wasn't explicitly clicked yet
    # Update session state to match
    st.session_state.query = user_query
    
    if user_query:
        with st.spinner("Searching knowledge base..."):
            try:
                response = requests.post(
                    API_URL, 
                    json={"query": user_query},
                    timeout=60
                )
                response.raise_for_status()
                data = response.json()
                
                st.markdown("### Answer")
                st.info(data.get("response"))
                
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to backend API: {e}")
                st.info("Make sure the FastAPI backend is running on http://localhost:8000")
