# 🎓 AI Lecture Assistant

AI-powered lecture learning assistant that transforms YouTube lectures into structured summaries, grounded Q&A, and interactive learning experiences using Retrieval-Augmented Generation (RAG).

---
<img width="3805" height="2039" alt="Screenshot 2026-05-21 114101" src="https://github.com/user-attachments/assets/74a458e0-f109-4599-92cc-680af74c3f64" />

<img width="3788" height="1857" alt="Screenshot 2026-05-21 114142" src="https://github.com/user-attachments/assets/4c840eee-6cbb-4abc-8def-be086b9224c8" />


# 🚀 Overview

AI Lecture Assistant enables users to:

* Extract transcripts from YouTube videos
* Automatically generate structured lecture summaries
* Ask grounded questions about lecture content
* Retrieve timestamp-aware contextual answers
* Process lectures with or without captions
* Prevent hallucinated AI responses using RAG

This project demonstrates a complete AI pipeline:

```text
YouTube Video
      ↓
Transcript Extraction
      ↓
Whisper Fallback (if captions unavailable)
      ↓
Chunking
      ↓
Embeddings Generation
      ↓
FAISS Vector Database
      ↓
Semantic Retrieval (RAG)
      ↓
Grounded LLM Responses
      ↓
Professional Streamlit UI
```

---

# ✨ Features

## 📄 Transcript Extraction

* Extracts YouTube captions automatically
* Supports:

  * Manual captions
  * Auto-generated captions
  * Videos without captions

---

## 🎙 Whisper AI Fallback

If captions are unavailable:

* Downloads audio using `yt-dlp`
* Transcribes using OpenAI Whisper
* Automatically switches to AI transcription

UI clearly indicates transcript source:

* ✅ YouTube Captions
* ⚠️ Whisper AI (generated from audio)

---

## 📝 AI Lecture Summaries

* Generates concise bullet-point summaries
* Supports:

  * Short lectures
  * Long lectures (20k–30k+ words)
* Uses hierarchical summarization for scalability

---

## 💬 Grounded Q&A

* Ask questions about lecture content
* Uses semantic retrieval (RAG)
* Answers ONLY from lecture context
* Prevents hallucinations and unsupported answers

---

## 🔍 Semantic Search

* SentenceTransformer embeddings
* FAISS vector similarity search
* Timestamp-aware retrieval

---

## 🧠 Hallucination Control

The assistant:

* NEVER uses outside knowledge
* ONLY answers from retrieved lecture context
* Rejects unsupported answers
* Detects speculative language

---

## 📊 Lecture Analytics

Displays:

* Word count
* Chunk count
* Transcript source
* Retrieved source context

---

# 🧠 Architecture

## End-to-End Flow

```text
YouTube URL
      ↓
Transcript Extraction
      ↓
YouTube Captions
        OR
Whisper Audio Transcription
      ↓
Transcript Cleaning
      ↓
Chunking
      ↓
Embeddings Generation
      ↓
FAISS Vector Store
      ↓
Semantic Retrieval
      ↓
Ollama + Mistral
      ↓
Grounded Answer Generation
      ↓
Streamlit Frontend
```

---

# 🛠 Tech Stack

## Frontend

* Streamlit

## Backend

* FastAPI

## LLM

* Ollama
* Mistral

## NLP / AI

* Sentence Transformers
* OpenAI Whisper

## Vector Database

* FAISS

## Data Source

* YouTube Transcript API
* yt-dlp

---

# 📂 Project Structure

```bash
AI-lecture-assistant/
│
├── app.py                     # Streamlit frontend
├── main.py                    # FastAPI backend
│
├── agents/
│   └── learning.py            # Summary + grounded Q&A
│
├── services/
│   ├── transcript.py          # Transcript extraction
│   └── rag.py                 # Chunking + FAISS retrieval
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# ⚙️ Installation

## 1. Clone Repository

```bash
git clone https://github.com/Amruth533/AI-lecture-assistant.git

cd AI-lecture-assistant
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

---

## 3. Install Requirements

```bash
pip install -r requirements.txt
```

---

# 🧠 Install Ollama

Download Ollama:

[https://ollama.com/download](https://ollama.com/download)

---

## Pull Mistral Model

```bash
ollama run mistral
```

This downloads and starts the local model.

---

# ▶️ Run The Application

## Terminal 1 — Start Ollama

```bash
ollama run mistral
```

---

## Terminal 2 — Start FastAPI Backend

```bash
uvicorn main:app --reload
```

---

## Terminal 3 — Start Streamlit Frontend

```bash
streamlit run app.py
```

---

# 📌 API Endpoints

## Health Check

```http
GET /
```

---

## Process Lecture

```http
POST /process
```

### Request

```json
{
  "url": "https://youtube.com/..."
}
```

---

## Ask Question

```http
POST /ask
```

### Request

```json
{
  "question": "What is supervised learning?"
}
```

---

# 🧪 Example Workflow

## Step 1

Paste YouTube lecture URL

## Step 2

Transcript extracted automatically

## Step 3

Lecture summarized into bullet points

## Step 4

Ask questions like:

* "What is gradient descent?"
* "What are neural networks?"
* "Explain overfitting."

## Step 5

Receive grounded AI answers with source context

---

# 🛡 Hallucination Prevention

This project uses multiple safeguards:

* Retrieval-Augmented Generation (RAG)
* Context-only prompting
* Similarity threshold filtering
* Speculative phrase detection
* Source-grounded responses

If information is unavailable, the assistant responds:

```text
This topic was not clearly covered in the lecture.
```

---

# 📈 Scalability Features

Supports:

* Long lectures
* 20k–30k+ word transcripts
* Multi-hour videos
* Podcasts
* Interviews
* Educational courses

Implemented using:

* Hierarchical summarization
* Chunk-based processing
* Semantic retrieval

---

# 🔮 Future Improvements

* Timestamp-click YouTube navigation
* Downloadable summaries
* Chat memory
* Multi-video knowledge base
* PDF/PPT support
* Cloud deployment
* Docker support
* Streaming responses
* Hybrid retrieval (BM25 + vector)

---

# 📸 Screenshots

*Add screenshots here later*

Example:

* Main UI
* Transcript source display
* Summary section
* Grounded Q&A
* Retrieved source context

---

# 🤝 Contributing

Contributions are welcome.

1. Fork repository
2. Create feature branch
3. Commit changes
4. Open pull request

---

# 📄 License

MIT License

---

# 👨‍💻 Author

Developed by Narasimha Vemuganti

AI Engineering • RAG Systems • NLP • Full Stack AI Applications
