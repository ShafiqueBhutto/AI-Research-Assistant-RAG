import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "document_id": None,
    "filename": None,
    "chunks_stored": 0,
    "session_id": None,
    "messages": [],
    "documents": [],
    "chat_sessions": [],
    "data_loaded": False
}


for key, value in DEFAULT_STATE.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# API HELPERS
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
            f"Could not load documents: "
            f"{response.text}"
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
            f"Could not load chat sessions: "
            f"{response.text}"
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

            st.error(
                "Chat session not found."
            )

            return None

        st.error(
            f"Could not load chat history: "
            f"{response.text}"
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

if not st.session_state["data_loaded"]:

    st.session_state["documents"] = (
        load_documents()
    )

    st.session_state["chat_sessions"] = (
        load_chat_sessions()
    )

    st.session_state["data_loaded"] = True


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🤖 AI Research Assistant")

    st.markdown("---")

    # ========================================================
    # UPLOAD DOCUMENT
    # ========================================================

    st.header("📄 Upload Document")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"]
    )

    if uploaded_file is not None:

        if st.button(
            "⬆️ Upload PDF",
            use_container_width=True
        ):

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

                        st.session_state[
                            "document_id"
                        ] = result["document_id"]

                        st.session_state[
                            "filename"
                        ] = result["filename"]

                        st.session_state[
                            "chunks_stored"
                        ] = result["chunks_stored"]

                        # New document = new conversation
                        st.session_state[
                            "session_id"
                        ] = None

                        st.session_state[
                            "messages"
                        ] = []

                        st.session_state[
                            "documents"
                        ] = load_documents()

                        st.session_state[
                            "chat_sessions"
                        ] = load_chat_sessions()

                        st.success(
                            "Document uploaded successfully!"
                        )

                        st.rerun()

                    else:

                        st.error(
                            f"Upload failed: "
                            f"{response.text}"
                        )

                except requests.exceptions.RequestException as e:

                    st.error(
                        f"Could not connect to FastAPI: {e}"
                    )

    # ========================================================
    # DOCUMENT MANAGEMENT
    # ========================================================

    st.markdown("---")

    st.header("📚 Documents")

    if st.button(
        "🔄 Refresh Documents",
        use_container_width=True
    ):

        st.session_state[
            "documents"
        ] = load_documents()

        st.rerun()

    documents = st.session_state[
        "documents"
    ]

    if documents:

        filenames = [
            document["filename"]
            for document in documents
        ]

        current_index = 0

        current_document_id = (
            st.session_state["document_id"]
        )

        for index, document in enumerate(
            documents
        ):

            if (
                document["document_id"]
                == current_document_id
            ):

                current_index = index

                break

        selected_filename = st.selectbox(
            "Select a document",
            filenames,
            index=current_index
        )

        selected_document = next(
            (
                document
                for document in documents
                if document["filename"]
                == selected_filename
            ),
            None
        )

        if selected_document:

            selected_document_id = (
                selected_document["document_id"]
            )

            # ------------------------------------------------
            # Document changed
            # ------------------------------------------------

            if (
                selected_document_id
                != st.session_state["document_id"]
            ):

                st.session_state[
                    "document_id"
                ] = selected_document_id

                st.session_state[
                    "filename"
                ] = selected_document["filename"]

                st.session_state[
                    "chunks_stored"
                ] = selected_document[
                    "chunks_stored"
                ]

                # New document -> new chat
                st.session_state[
                    "session_id"
                ] = None

                st.session_state[
                    "messages"
                ] = []

                st.rerun()

            st.caption(
                "📄 Selected Document"
            )

            st.write(
                selected_document["filename"]
            )

            st.caption(
                f"Chunks stored: "
                f"{selected_document['chunks_stored']}"
            )

            # ------------------------------------------------
            # Delete document
            # ------------------------------------------------

            if st.button(
                "🗑️ Delete Selected Document",
                use_container_width=True
            ):

                document_id = (
                    selected_document[
                        "document_id"
                    ]
                )

                try:

                    response = requests.delete(
                        f"{API_URL}/documents/"
                        f"{document_id}",
                        timeout=60
                    )

                    if response.status_code == 200:

                        st.session_state[
                            "document_id"
                        ] = None

                        st.session_state[
                            "filename"
                        ] = None

                        st.session_state[
                            "chunks_stored"
                        ] = 0

                        st.session_state[
                            "session_id"
                        ] = None

                        st.session_state[
                            "messages"
                        ] = []

                        st.session_state[
                            "documents"
                        ] = load_documents()

                        st.session_state[
                            "chat_sessions"
                        ] = load_chat_sessions()

                        st.success(
                            "Document deleted successfully!"
                        )

                        st.rerun()

                    else:

                        st.error(
                            f"Delete failed: "
                            f"{response.text}"
                        )

                except requests.exceptions.RequestException as e:

                    st.error(
                        f"Could not connect to FastAPI: {e}"
                    )

    else:

        st.info(
            "No documents uploaded yet."
        )

    # ========================================================
    # PREVIOUS CHATS
    # ========================================================

    st.markdown("---")

    st.header("💬 Previous Chats")

    if st.button(
        "🔄 Refresh Chats",
        use_container_width=True
    ):

        st.session_state[
            "chat_sessions"
        ] = load_chat_sessions()

        st.rerun()

    chat_sessions = st.session_state[
        "chat_sessions"
    ]

    if chat_sessions:

        chat_titles = []

        chat_mapping = {}

        for session in chat_sessions:

            title = session.get(
                "title",
                "New Chat"
            )

            display_title = title

            if len(display_title) > 45:

                display_title = (
                    display_title[:45]
                    + "..."
                )

            display = (
                f"💬 {display_title}"
            )

            chat_titles.append(display)

            chat_mapping[display] = (
                session["session_id"]
            )

        selected_chat = st.selectbox(
            "Select a previous chat",
            chat_titles
        )

        selected_session_id = (
            chat_mapping[selected_chat]
        )

        if st.button(
            "📂 Open Chat",
            use_container_width=True
        ):

            history = load_chat_history(
                selected_session_id
            )

            if history:

                st.session_state[
                    "session_id"
                ] = history["session_id"]

                st.session_state[
                    "messages"
                ] = []

                # --------------------------------------------
                # Restore conversation
                # --------------------------------------------

                for message in history.get(
                    "messages",
                    []
                ):

                    st.session_state[
                        "messages"
                    ].append(
                        {
                            "question": message[
                                "question"
                            ],
                            "answer": message[
                                "answer"
                            ],
                            "sources": message.get(
                                "sources",
                                []
                            )
                        }
                    )

                # --------------------------------------------
                # Restore document
                # --------------------------------------------

                document_id = history.get(
                    "document_id"
                )

                if document_id:

                    document = (
                        get_document_by_id(
                            document_id
                        )
                    )

                    if document:

                        st.session_state[
                            "document_id"
                        ] = document[
                            "document_id"
                        ]

                        st.session_state[
                            "filename"
                        ] = document[
                            "filename"
                        ]

                        st.session_state[
                            "chunks_stored"
                        ] = document[
                            "chunks_stored"
                        ]

                st.rerun()

    else:

        st.info(
            "No previous chats yet."
        )

    # ========================================================
    # NEW CHAT
    # ========================================================

    st.markdown("---")

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        st.session_state[
            "session_id"
        ] = None

        st.session_state[
            "messages"
        ] = []

        st.rerun()


# ============================================================
# MAIN PAGE
# ============================================================

st.title("🤖 AI Research Assistant")

st.markdown(
    """
    Upload a PDF and ask questions about its content.

    **RAG (Retrieval-Augmented Generation)** retrieves
    relevant information from your documents and generates
    grounded answers with source references.
    """
)


# ============================================================
# CURRENT DOCUMENT
# ============================================================

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

    st.warning(
        "📄 Please upload or select a document first."
    )


# ============================================================
# CHAT HEADER
# ============================================================

st.header("💬 Ask a Question")


# ============================================================
# TOP K
# ============================================================

top_k = st.slider(
    "Number of relevant chunks",
    min_value=1,
    max_value=5,
    value=3
)


# ============================================================
# DISPLAY EXISTING CHAT
# ============================================================

for message in st.session_state["messages"]:

    with st.chat_message("user"):

        st.markdown(
            message["question"]
        )

    with st.chat_message("assistant"):

        st.markdown(
            message["answer"]
        )

        sources = message.get(
            "sources",
            []
        )

        if sources:

            with st.expander(
                f"📚 Sources ({len(sources)})"
            ):

                for index, source in enumerate(
                    sources,
                    start=1
                ):

                    filename = source.get(
                        "filename",
                        "Unknown"
                    )

                    page = source.get(
                        "page",
                        "Unknown"
                    )

                    distance = source.get(
                        "distance",
                        0
                    )

                    st.markdown(
                        f"""
**Source {index}**

📄 File: `{filename}`

📑 Page: `{page}`

🔎 Distance: `{distance:.4f}`
"""
                    )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask something about your document..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    question = question.strip()

    if not question:

        st.warning(
            "Please enter a question."
        )

        st.stop()

    if not st.session_state[
        "document_id"
    ]:

        st.warning(
            "Please upload or select a PDF document first."
        )

        st.stop()

    # --------------------------------------------------------
    # Display user message immediately
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(
            question
        )

    # --------------------------------------------------------
    # Generate answer
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Searching the document..."
        ):

            try:

                request_data = {
                    "question": question,
                    "top_k": top_k,
                    "document_id": (
                        st.session_state[
                            "document_id"
                        ]
                    )
                }

                # --------------------------------------------
                # Continue existing chat
                # --------------------------------------------

                if st.session_state[
                    "session_id"
                ]:

                    request_data[
                        "session_id"
                    ] = st.session_state[
                        "session_id"
                    ]

                response = requests.post(
                    f"{API_URL}/chat",
                    json=request_data,
                    timeout=120
                )

                # --------------------------------------------
                # Successful response
                # --------------------------------------------

                if response.status_code == 200:

                    result = response.json()

                    answer = result.get(
                        "answer",
                        "No answer generated."
                    )

                    sources = result.get(
                        "sources",
                        []
                    )

                    # ----------------------------------------
                    # Save session ID
                    # ----------------------------------------

                    st.session_state[
                        "session_id"
                    ] = result[
                        "session_id"
                    ]

                    # ----------------------------------------
                    # Save message locally
                    # ----------------------------------------

                    st.session_state[
                        "messages"
                    ].append(
                        {
                            "question": question,
                            "answer": answer,
                            "sources": sources
                        }
                    )

                    # ----------------------------------------
                    # Show answer
                    # ----------------------------------------

                    st.markdown(
                        answer
                    )

                    # ----------------------------------------
                    # Show sources
                    # ----------------------------------------

                    if sources:

                        with st.expander(
                            f"📚 Sources "
                            f"({len(sources)})"
                        ):

                            for index, source in enumerate(
                                sources,
                                start=1
                            ):

                                filename = source.get(
                                    "filename",
                                    "Unknown"
                                )

                                page = source.get(
                                    "page",
                                    "Unknown"
                                )

                                distance = source.get(
                                    "distance",
                                    0
                                )

                                st.markdown(
                                    f"""
**Source {index}**

📄 File: `{filename}`

📑 Page: `{page}`

🔎 Distance: `{distance:.4f}`
"""
                                )

                    # ----------------------------------------
                    # Refresh chat list
                    # ----------------------------------------

                    st.session_state[
                        "chat_sessions"
                    ] = load_chat_sessions()

                else:

                    try:

                        error_detail = (
                            response.json()
                            .get(
                                "detail",
                                response.text
                            )
                        )

                    except Exception:

                        error_detail = response.text

                    st.error(
                        f"Chat request failed: "
                        f"{error_detail}"
                    )

            except requests.exceptions.Timeout:

                st.error(
                    "The request took too long. "
                    "Please try again."
                )

            except requests.exceptions.RequestException as e:

                st.error(
                    f"Could not connect to FastAPI: {e}"
                )

            except Exception as e:

                st.error(
                    f"Unexpected error: {str(e)}"
                )