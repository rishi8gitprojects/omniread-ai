# interface.py
import os
import streamlit as st
from dotenv import load_dotenv

# Import your database and chatbot functions exactly from your file structure
from Embeddings.vector_db import chunk_and_store
from Embeddings.chatbot import handle_semantic_query

# Load local environment token flags
load_dotenv()
HF_TOKEN = os.getenv("GROQ_API_KEY")

# 1. Page Configuration Setup
st.set_page_config(page_title="English Research Assistant", page_icon="?", layout="wide")
st.title("📚 English Studies Textual & Rhetorical Analyst")
st.subheader("Advanced RAG Workspace for Literary Analysts")

# 2. Document Ingestion Section (The Missing Part)
# We wrap this in an st.expander layout to keep the workspace clean
with st.expander("📁 Document Ingestion System Workspace", expanded=True):
    uploaded_file = st.file_uploader(
        "Upload a literary text, manuscript, or document corpus (PDF format only):", 
        type=["pdf"]
    )
    
    if uploaded_file is not None:
        # Check if this specific document has already been processed in this session
        if "processed_filename" not in st.session_state or st.session_state.processed_filename != uploaded_file.name:
            with st.spinner(f"Reading string streams and indexing elements from '{uploaded_file.name}' into vector space..."):
                try:
                    # Read the file directly into a byte stream array
                    pdf_bytes = uploaded_file.read()
                    
                    # Call function 2 from your vector_db.py process pipeline
                    total_chunks = chunk_and_store(pdf_bytes, uploaded_file.name)
                    
                    if total_chunks > 0:
                        st.success(f"Successfully processed manuscript! Indexed {total_chunks} structural vectors inside Chroma.")
                        st.session_state.processed_filename = uploaded_file.name
                    else:
                        st.warning("The uploaded file could not be broken into readable elements. Confirm formatting.")
                except Exception as e:
                    st.error(f"Failed to execute vector indexing pipeline: {str(e)}")

# 3. Maintain Conversational Chat Session History States
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 4. Render Active Discussion Blocks Continuously on UI Updates
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Interactive Chat Core Workflow Control Loop
if user_query := st.chat_input("Ask a question regarding structural metrics, macro character sketches, themes, or citations..."):
    
    # Immediately log and render user query locally
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.chat_history.append({"role": "user", "content": user_query})

    # Execute backend analysis generation pipeline area
    with st.chat_message("assistant"):
        with st.spinner("Analyzing linguistic structures and processing context matrices..."):
            try:
                # FIXED: We now pass st.session_state.chat_history directly to the chatbot 
                # so your memory tool wrapper function can look over previous statement nodes.
                explanation_output = handle_semantic_query(
                    user_query=user_query, 
                    chat_history=st.session_state.chat_history[:-1], # pass everything except current prompt
                    hf_token=HF_TOKEN
                )
                
                # Display final academic-grade analytical prose block
                st.markdown(explanation_output)
                
                # Commit conversation changes to state
                st.session_state.chat_history.append({"role": "assistant", "content": explanation_output})
            except Exception as e:
                st.error(f"An processing break error occurred: {str(e)}")