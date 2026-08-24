import requests
import streamlit as st


# -----------------------------
# Configuration
# -----------------------------

API_URL = "http://127.0.0.1:8000"


# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🤖",
    layout="wide"
)


# -----------------------------
# Title
# -----------------------------

st.title("🤖 AI Research Assistant")

st.markdown(
    """
    Upload a PDF document and ask questions about its content.
    
    The system uses **RAG (Retrieval-Augmented Generation)** to retrieve
    relevant information from your documents and generate grounded answers.
    """
)


# -----------------------------
# Sidebar - Document Upload
# -----------------------------

st.sidebar.header("📄 Upload Document")

uploaded_file = st.sidebar.file_uploader(
    "Choose a PDF file",
    type=["pdf"]
)


if uploaded_file is not None:

    if st.sidebar.button("Upload PDF"):

        with st.sidebar:
            with st.spinner("Uploading and processing document..."):

                try:

                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    }

                    response = requests.post(
                        f"{API_URL}/documents/upload",
                        files=files,
                        timeout=120
                    )

                    if response.status_code == 200:

                        result = response.json()

                        st.success(
                            "Document uploaded successfully!"
                        )

                        st.session_state["document_id"] = (
                            result["document_id"]
                        )

                        st.session_state["filename"] = (
                            result["filename"]
                        )

                        st.session_state["chunks_stored"] = (
                            result["chunks_stored"]
                        )

                    else:

                        st.error(
                            f"Upload failed: {response.text}"
                        )

                except requests.exceptions.RequestException as e:

                    st.error(
                        f"Could not connect to FastAPI: {e}"
                    )


# -----------------------------
# Document Information
# -----------------------------

if "filename" in st.session_state:

    st.info(
        f"📄 Current document: "
        f"**{st.session_state['filename']}**"
    )

    st.caption(
        f"Chunks stored: "
        f"{st.session_state['chunks_stored']}"
    )


# -----------------------------
# Chat Section
# -----------------------------

st.header("💬 Ask a Question")

question = st.text_input(
    "Enter your question",
    placeholder="Example: What skills does Shafique Bhutto have?"
)


top_k = st.slider(
    "Number of relevant chunks",
    min_value=1,
    max_value=5,
    value=3
)


if st.button("🔍 Ask"):

    if not question.strip():

        st.warning("Please enter a question.")

    else:

        with st.spinner("Searching documents and generating answer..."):

            try:

                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "question": question,
                        "top_k": top_k,
                        "document_id": st.session_state.get("document_id")
                    },
                    timeout=120
                )

                if response.status_code == 200:

                    result = response.json()

                    # -----------------------------
                    # Answer
                    # -----------------------------

                    st.subheader("🤖 Answer")

                    st.markdown(
                        result["answer"]
                    )

                    # -----------------------------
                    # Sources
                    # -----------------------------

                    st.subheader("📚 Sources")

                    sources = result.get("sources", [])

                    if sources:

                        for i, source in enumerate(
                            sources,
                            start=1
                        ):

                            st.markdown(
                                f"""
                                **Source {i}**

                                - 📄 File: `{source['filename']}`
                                - 📑 Page: `{source['page']}`
                                - 🔎 Distance: `{source['distance']:.4f}`
                                """
                            )

                            st.divider()

                    else:

                        st.info(
                            "No sources were returned."
                        )

                else:

                    st.error(
                        f"Chat request failed: {response.text}"
                    )

            except requests.exceptions.RequestException as e:

                st.error(
                    f"Could not connect to FastAPI: {e}"
                )