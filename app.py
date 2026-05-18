import streamlit as st
import requests

# 🔥 PAGE CONFIG
st.set_page_config(
    page_title="AK Lecture Assistant",
    layout="wide"
)

# 🎨 HEADER
st.markdown("""
<h1 style='margin-bottom:0;'>AK Lecture Assistant</h1>
<p style='color:gray;'>Learn from lectures using AI-powered summaries and contextual Q&A.</p>
""", unsafe_allow_html=True)

# SESSION STATE
if "summary" not in st.session_state:
    st.session_state.summary = None

if "transcript" not in st.session_state:
    st.session_state.transcript = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 📥 SIDEBAR INPUT
with st.sidebar:
    st.header("📥 Input")

    url = st.text_input("YouTube URL")

    process_btn = st.button("🚀 Process Lecture")

# MAIN LAYOUT
left, right = st.columns([1, 2])

# 🚀 PROCESS
if process_btn:
    try:
        with st.spinner("Analyzing lecture..."):
            res = requests.post(
                "http://127.0.0.1:8000/process",
                params={"url": url},
                timeout=30
            )

        data = res.json()

        if "error" in data:
            st.error(data["error"])
        else:
            st.success("Lecture processed successfully!")

            st.session_state.summary = data["summary"]
            st.session_state.transcript = data["full_text"]
            st.session_state.chat_history = []

    except Exception as e:
        st.error(str(e))

# 📊 LEFT COLUMN (Stats)
with left:
    if st.session_state.transcript:
        st.markdown("### 📊 Lecture Stats")
        st.write(f"Words: {len(st.session_state.transcript.split())}")

# 📝 RIGHT COLUMN (Summary)
with right:
    if st.session_state.summary:
        st.markdown("## 📝 Summary")
        st.write(st.session_state.summary)

# 📚 TABS (Chat + Transcript)
if st.session_state.transcript:

    tab1, tab2 = st.tabs(["💬 Chat", "📄 Transcript"])

    # 💬 CHAT TAB
    with tab1:
        st.subheader("Ask Questions")

        # Display chat
        for chat in st.session_state.chat_history:
            with st.chat_message(chat["role"]):
                st.write(chat["message"])

        question = st.chat_input("Ask something about the lecture")

        if question:
            # Save user message
            st.session_state.chat_history.append({
                "role": "user",
                "message": question
            })

            with st.chat_message("user"):
                st.write(question)

            try:
                with st.spinner("Thinking..."):
                    res = requests.post(
                        "http://127.0.0.1:8000/ask",
                        params={"question": question},
                        timeout=30
                    )

                data = res.json()

                if "error" in data:
                    st.error(data["error"])
                else:
                    answer = data["answer"]

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "message": answer
                    })

                    with st.chat_message("assistant"):
                        st.write(answer)

                    with st.expander("📌 Source"):
                        st.write(data["source"])

            except Exception as e:
                st.error(str(e))

    # 📄 TRANSCRIPT TAB
    with tab2:
        st.text_area("Transcript", st.session_state.transcript, height=400)