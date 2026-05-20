# app.py

import streamlit as st
import requests


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Lecture Assistant",
    page_icon="🎓",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .stButton button {
        width: 100%;
        height: 3rem;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 600;
    }

    .answer-box {
        background-color: #111827;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #374151;
        margin-top: 10px;
    }

    .source-box {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.title("🎓 AI Lecture Assistant")

st.caption(
    "AI-powered lecture summarization and grounded Q&A"
)


# ============================================================
# SESSION STATE
# ============================================================

if "processed" not in st.session_state:
    st.session_state.processed = False

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "stats" not in st.session_state:
    st.session_state.stats = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Features")

    st.markdown("""
    ✅ Transcript Extraction  
    ✅ AI Summarization  
    ✅ Grounded Q&A  
    ✅ RAG Architecture  
    ✅ FAISS Retrieval  
    ✅ Timestamp Context  
    ✅ Hallucination Control  
    """)

    st.divider()

    st.info(
        "Answers are generated ONLY "
        "from lecture transcript context."
    )


# ============================================================
# YOUTUBE URL INPUT
# ============================================================

url = st.text_input(
    "📺 Enter YouTube Lecture URL"
)


# ============================================================
# PROCESS BUTTON
# ============================================================

if st.button("🚀 Process Lecture"):

    if not url:

        st.warning("Please enter a valid YouTube URL.")

    else:

        with st.spinner(
            "Processing lecture..."
        ):

            try:

                response = requests.post(
                    "http://127.0.0.1:8000/process",
                    json={"url": url},
                    timeout=300
                )

                data = response.json()

                if "error" in data:

                    st.error(data["error"])

                else:

                    st.session_state.processed = True

                    st.session_state.summary = data["summary"]

                    st.session_state.transcript = (
                        data["transcript"]
                    )

                    st.session_state.stats = (
                        data["stats"]
                    )

                    st.success(
                        "Lecture processed successfully!"
                    )

            except Exception as e:

                st.error(f"Error: {str(e)}")


# ============================================================
# DISPLAY RESULTS
# ============================================================

if st.session_state.processed:

    col1, col2 = st.columns([1, 1])

    # --------------------------------------------------------
    # LEFT SIDE
    # --------------------------------------------------------

    with col1:

        st.subheader("📌 Lecture Summary")

        st.markdown(
            st.session_state.summary
        )

        st.divider()

        st.subheader("📊 Lecture Statistics")

        stats = st.session_state.stats

        col_a, col_b = st.columns(2)

        with col_a:

            st.metric(
                "Words",
                stats.get("word_count", 0)
            )

        with col_b:

            st.metric(
                "Chunks",
                stats.get("chunk_count", 0)
            )

    # --------------------------------------------------------
    # RIGHT SIDE
    # --------------------------------------------------------

    with col2:

        st.subheader("📄 Transcript")

        st.text_area(
            "Transcript",
            st.session_state.transcript,
            height=500
        )


# ============================================================
# Q&A SECTION
# ============================================================

st.divider()

st.subheader("💬 Ask Questions")

question = st.text_input(
    "Ask a question about the lecture"
)


# ============================================================
# ASK BUTTON
# ============================================================

if st.button("Ask AI"):

    if not st.session_state.processed:

        st.warning(
            "Please process a lecture first."
        )

    elif not question:

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Generating grounded answer..."
        ):

            try:

                response = requests.post(
                    "http://127.0.0.1:8000/ask",
                    json={
                        "question": question
                    },
                    timeout=300
                )

                data = response.json()

                if "error" in data:

                    st.error(data["error"])

                else:

                    answer = data.get(
                        "answer",
                        "No answer generated."
                    )

                    sources = data.get(
                        "sources",
                        []
                    )

                    # ------------------------------------
                    # SAVE CHAT HISTORY
                    # ------------------------------------

                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer,
                        "sources": sources
                    })

            except Exception as e:

                st.error(f"Error: {str(e)}")


# ============================================================
# CHAT HISTORY
# ============================================================

if st.session_state.chat_history:

    st.divider()

    st.subheader("🧠 Conversation")

    for chat in reversed(
        st.session_state.chat_history
    ):

        st.markdown(
            f"### ❓ {chat['question']}"
        )

        st.markdown(
            f"""
            <div class="answer-box">
            {chat['answer']}
            </div>
            """,
            unsafe_allow_html=True
        )

        # ----------------------------------------------------
        # SOURCES
        # ----------------------------------------------------

        if chat["sources"]:

            with st.expander(
                "📚 Retrieved Lecture Context"
            ):

                for source in chat["sources"]:

                    timestamp = round(
                        source["start"] / 60,
                        2
                    )

                    st.markdown(
                        f"""
                        <div class="source-box">

                        <b>Timestamp:</b>
                        {timestamp} min

                        <br><br>

                        <b>Similarity Score:</b>
                        {round(source['score'], 3)}

                        <br><br>

                        <b>Lecture Context:</b>

                        {source['text']}

                        </div>
                        """,
                        unsafe_allow_html=True
                    )