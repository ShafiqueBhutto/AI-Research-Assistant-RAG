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
# Initialize Session State
# -----------------------------

if "document_id" not in st.session_state:
    st.session_state["document_id"] = None

if "filename" not in st.session_state:
    st.session_state["filename"] = None

if "chunks_stored" not in st.session_state:
    st.session_state["chunks_stored"] = 0

if "session_id" not in st.session_state:
    st.session_state["session_id"] = None

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "documents" not in st.session_state:
    st.session_state["documents"] = []

if "chat_sessions" not in st.session_state:
    st.session_state["chat_sessions"] = []


# ============================================================
# HELPER FUNCTIONS
# ============================================================


def load_documents():

    try:

        response = requests.get(
            f"{API_URL}/documents",
            timeout=30
        )

        if response.status_code == 200:
            return response.json()

        st.error(
            f"Could not load documents: {response.text}"
        )

        return []

    except requests.exceptions.RequestException as e:

        st.error(
            f"Could not connect to FastAPI: {e}"
        )

        return []


def load_chat_sessions():

    try:

        response = requests.get(
            f"{API_URL}/chat",
            timeout=30
        )

        if response.status_code == 200:
            return response.json()

        st.error(
            f"Could not load chat sessions: {response.text}"
        )

        return []

    except requests.exceptions.RequestException as e:

        st.error(
            f"Could not connect to FastAPI: {e}"
        )

        return []


def load_chat_history(session_id):

    try:

        response = requests.get(
            f"{API_URL}/chat/{session_id}",
            timeout=30
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 404:
            st.error("Chat session not found.")
            return None

        st.error(
            f"Could not load chat history: {response.text}"
        )

        return None

    except requests.exceptions.RequestException as e:

        st.error(
            f"Could not connect to FastAPI: {e}"
        )

        return None


def get_document_by_id(document_id):

    try:

        response = requests.get(
            f"{API_URL}/documents/{document_id}",
            timeout=30
        )

        if response.status_code == 200:
            return response.json()

        return None

    except requests.exceptions.RequestException:
        return None


# ============================================================
# INITIAL DATA LOAD
# ============================================================


if not st.session_state["documents"]:

    st.session_state["documents"] = load_documents()


if not st.session_state["chat_sessions"]:

    st.session_state["chat_sessions"] = load_chat_sessions()


# ============================================================
# TITLE
# ============================================================


st.title("🤖 AI Research Assistant")

st.markdown(
    """
    Upload a PDF document and ask questions about its content.

    The system uses **RAG (Retrieval-Augmented Generation)** to retrieve
    relevant information from your documents and generate grounded answers.
    """
)


# ============================================================
# SIDEBAR
# ============================================================


# -----------------------------
# Upload Document
# -----------------------------

st.sidebar.header("📄 Upload Document")

uploaded_file = st.sidebar.file_uploader(
    "Choose a PDF file",
    type=["pdf"]
)


if uploaded_file is not None:

    if st.sidebar.button(
        "Upload PDF",
        use_container_width=True
    ):

        with st.sidebar:

            with st.spinner(
                "Uploading and processing document..."
            ):

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

                        # Save current document
                        st.session_state["document_id"] = (
                            result["document_id"]
                        )

                        st.session_state["filename"] = (
                            result["filename"]
                        )

                        st.session_state["chunks_stored"] = (
                            result["chunks_stored"]
                        )

                        # Start fresh conversation
                        st.session_state["session_id"] = None
                        st.session_state["messages"] = []

                        # Refresh data
                        st.session_state["documents"] = (
                            load_documents()
                        )

                        st.session_state["chat_sessions"] = (
                            load_chat_sessions()
                        )

                        st.success(
                            "Document uploaded successfully!"
                        )

                    else:

                        st.error(
                            f"Upload failed: {response.text}"
                        )

                except requests.exceptions.RequestException as e:

                    st.error(
                        f"Could not connect to FastAPI: {e}"
                    )


# ============================================================
# DOCUMENT MANAGEMENT
# ============================================================


st.sidebar.markdown("---")

st.sidebar.header("📚 Documents")


# -----------------------------
# Refresh Documents
# -----------------------------

if st.sidebar.button(
    "🔄 Refresh Documents",
    use_container_width=True
):

    st.session_state["documents"] = load_documents()

    st.rerun()


documents = st.session_state["documents"]


# -----------------------------
# Document Selection
# -----------------------------

if documents:

    document_options = {
        document["filename"]: document["document_id"]
        for document in documents
    }

    filenames = list(document_options.keys())

    current_index = 0

    if st.session_state["document_id"]:

        for index, document in enumerate(documents):

            if (
                document["document_id"]
                == st.session_state["document_id"]
            ):

                current_index = index
                break

    selected_filename = st.sidebar.selectbox(
        "Select a document",
        filenames,
        index=current_index
    )

    selected_document_id = document_options[
        selected_filename
    ]

    # -----------------------------
    # Detect document change
    # -----------------------------

    if (
        selected_document_id
        != st.session_state["document_id"]
    ):

        selected_document = next(
            (
                document
                for document in documents
                if document["document_id"]
                == selected_document_id
            ),
            None
        )

        if selected_document:

            st.session_state["document_id"] = (
                selected_document["document_id"]
            )

            st.session_state["filename"] = (
                selected_document["filename"]
            )

            st.session_state["chunks_stored"] = (
                selected_document["chunks_stored"]
            )

            # New document = fresh conversation
            st.session_state["session_id"] = None
            st.session_state["messages"] = []

    # -----------------------------
    # Selected Document
    # -----------------------------

    selected_document = next(
        (
            document
            for document in documents
            if document["document_id"]
            == st.session_state["document_id"]
        ),
        None
    )

    if selected_document:

        st.sidebar.caption(
            "📄 Selected Document"
        )

        st.sidebar.write(
            selected_document["filename"]
        )

        st.sidebar.caption(
            f"Chunks stored: "
            f"{selected_document['chunks_stored']}"
        )

        # -----------------------------
        # Delete Document
        # -----------------------------

        if st.sidebar.button(
            "🗑️ Delete Selected Document",
            use_container_width=True
        ):

            document_id = (
                selected_document["document_id"]
            )

            try:

                response = requests.delete(
                    f"{API_URL}/documents/{document_id}",
                    timeout=60
                )

                if response.status_code == 200:

                    st.session_state["document_id"] = None
                    st.session_state["filename"] = None
                    st.session_state["chunks_stored"] = 0

                    st.session_state["session_id"] = None
                    st.session_state["messages"] = []

                    st.session_state["documents"] = (
                        load_documents()
                    )

                    st.session_state["chat_sessions"] = (
                        load_chat_sessions()
                    )

                    st.success(
                        "Document deleted successfully!"
                    )

                    st.rerun()

                elif response.status_code == 404:

                    st.error(
                        "Document not found."
                    )

                else:

                    st.error(
                        f"Delete failed: {response.text}"
                    )

            except requests.exceptions.RequestException as e:

                st.error(
                    f"Could not connect to FastAPI: {e}"
                )

else:

    st.sidebar.info(
        "No documents uploaded yet."
    )


# ============================================================
# PREVIOUS CHATS
# ============================================================


st.sidebar.markdown("---")

st.sidebar.header("💬 Previous Chats")


# -----------------------------
# Refresh Chats
# -----------------------------

if st.sidebar.button(
    "🔄 Refresh Chats",
    use_container_width=True
):

    st.session_state["chat_sessions"] = (
        load_chat_sessions()
    )

    st.rerun()


chat_sessions = st.session_state["chat_sessions"]


# -----------------------------
# Previous Chat Selection
# -----------------------------

if chat_sessions:

    chat_options = {}

    for session in chat_sessions:

        title = session.get(
            "title",
            "New Chat"
        )

        session_id = session["session_id"]

        # Add small identifier in case
        # multiple chats have same title
        display_title = title

        if len(display_title) > 45:
            display_title = (
                display_title[:45] + "..."
            )

        chat_options[
            f"💬 {display_title}"
        ] = session_id


    selected_chat_title = st.sidebar.selectbox(
        "Select a previous chat",
        list(chat_options.keys())
    )


    selected_session_id = chat_options[
        selected_chat_title
    ]


    # -----------------------------
    # Load Selected Chat
    # -----------------------------

    if st.sidebar.button(
        "📂 Open Chat",
        use_container_width=True
    ):

        history = load_chat_history(
            selected_session_id
        )

        if history:

            st.session_state["session_id"] = (
                history["session_id"]
            )

            st.session_state["messages"] = []

            for message in history.get(
                "messages",
                []
            ):

                st.session_state["messages"].append(
                    {
                        "question": message["question"],
                        "answer": message["answer"],
                        "sources": message.get(
                            "sources",
                            []
                        )
                    }
                )


            # Restore associated document
            document_id = history.get(
                "document_id"
            )

            if document_id:

                document = get_document_by_id(
                    document_id
                )

                if document:

                    st.session_state["document_id"] = (
                        document["document_id"]
                    )

                    st.session_state["filename"] = (
                        document["filename"]
                    )

                    st.session_state["chunks_stored"] = (
                        document["chunks_stored"]
                    )


            st.success(
                "Previous chat loaded successfully!"
            )

            st.rerun()


else:

    st.sidebar.info(
        "No previous chats yet."
    )


# ============================================================
# NEW CHAT
# ============================================================


st.sidebar.markdown("---")


if st.sidebar.button(
    "➕ New Chat",
    use_container_width=True
):

    st.session_state["session_id"] = None
    st.session_state["messages"] = []

    st.rerun()


# ============================================================
# ACTIVE CHAT SESSION
# ============================================================


if st.session_state["session_id"]:

    st.sidebar.markdown("---")

    st.sidebar.caption(
        "💬 Active Chat Session"
    )

    st.sidebar.code(
        st.session_state["session_id"]
    )


# ============================================================
# MAIN CONTENT
# ============================================================


# -----------------------------
# Current Document
# -----------------------------

if st.session_state["filename"]:

    st.info(
        f"📄 Current document: "
        f"**{st.session_state['filename']}**"
    )

    st.caption(
        f"Chunks stored: "
        f"{st.session_state['chunks_stored']}"
    )

else:

    st.info(
        "📄 Please upload or select a document to start."
    )


# ============================================================
# CHAT
# ============================================================


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


# -----------------------------
# Ask Question
# -----------------------------


if st.button("🔍 Ask"):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    elif not st.session_state["document_id"]:

        st.warning(
            "Please upload or select a PDF document first."
        )

    else:

        with st.spinner(
            "Searching documents and generating answer..."
        ):

            try:

                request_data = {
                    "question": question,
                    "top_k": top_k,
                    "document_id": (
                        st.session_state["document_id"]
                    )
                }


                if st.session_state["session_id"]:

                    request_data["session_id"] = (
                        st.session_state["session_id"]
                    )


                response = requests.post(
                    f"{API_URL}/chat",
                    json=request_data,
                    timeout=120
                )


                if response.status_code == 200:

                    result = response.json()


                    # Save session ID
                    st.session_state["session_id"] = (
                        result["session_id"]
                    )


                    # Save message
                    st.session_state["messages"].append(
                        {
                            "question": question,
                            "answer": result["answer"],
                            "sources": result.get(
                                "sources",
                                []
                            )
                        }
                    )


                    # Refresh previous chats
                    st.session_state["chat_sessions"] = (
                        load_chat_sessions()
                    )


                    st.success(
                        "Answer generated successfully!"
                    )


                else:

                    st.error(
                        f"Chat request failed: {response.text}"
                    )


            except requests.exceptions.RequestException as e:

                st.error(
                    f"Could not connect to FastAPI: {e}"
                )


# ============================================================
# CONVERSATION HISTORY
# ============================================================


if st.session_state["messages"]:

    st.header("💬 Conversation")


    for i, message in enumerate(
        st.session_state["messages"],
        start=1
    ):

        st.markdown(
            f"### 👤 Question {i}"
        )

        st.markdown(
            message["question"]
        )


        st.markdown(
            "### 🤖 Answer"
        )

        st.markdown(
            message["answer"]
        )


        # -----------------------------
        # Sources
        # -----------------------------

        sources = message.get(
            "sources",
            []
        )


        if sources:

            st.markdown(
                "### 📚 Sources"
            )


            for source_index, source in enumerate(
                sources,
                start=1
            ):

                st.markdown(
                    f"""
                    **Source {source_index}**

                    - 📄 File: `{source.get("filename")}`
                    - 📑 Page: `{source.get("page")}`
                    - 🔎 Distance: `{source.get("distance", 0):.4f}`
                    """
                )


        st.divider()