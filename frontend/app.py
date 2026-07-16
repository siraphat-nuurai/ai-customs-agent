import streamlit as st
import requests

st.set_page_config(page_title="Customs & Import Duty Agent", page_icon="🚢", layout="wide")

API_URL = "http://backend:8000/api"

# --- Sidebar: Admin Document Ingestion ---
with st.sidebar:
    st.header("Admin Settings")
    st.subheader("📚 Update Tariff Database (RAG)")
    uploaded_file = st.file_uploader("Upload HS Code / Tariff Docs (PDF/TXT)", type=["pdf", "txt"])
    
    if st.button("Ingest Document") and uploaded_file is not None:
        with st.spinner("Processing document..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            try:
                response = requests.post(f"{API_URL}/ingest", files=files)
                if response.status_code == 200:
                    st.success(f"Successfully processed {response.json().get('chunks_processed')} chunks!")
                else:
                    st.error(f"Error: {response.json().get('detail')}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")
                
    st.divider()
    if st.button("🧹 Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- Main Chat Interface ---
st.title("🚢 AI Customs & Import Duty Agent")
st.caption("Enterprise-grade decoupled RAG architecture with Math, Web Search, and Compliance Guardrails.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("E.g., 'Calculate duty for $1000 laptop. Shipping $50. Check current HS rules.'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consulting guidelines and calculating duty..."):
            try:
                payload = {
                    "query": prompt,
                    "history": st.session_state.messages[:-1] # Exclude the current prompt
                }
                response = requests.post(f"{API_URL}/query", json=payload, timeout=60)
                
                if response.status_code == 200:
                    answer = response.json().get("response")
                else:
                    answer = f"**System Warning:** {response.json().get('detail', 'Unknown error occurred.')}"
                    
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the FastAPI Backend. Ensure Docker containers are running.")