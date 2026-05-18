# Lecture AI

AI-powered learning assistant that transforms lecture videos into structured insights and interactive conversations.

---

## 🚀 Overview

AK Lecture Assistant allows users to:
- Extract transcripts from YouTube lectures
- Generate concise summaries
- Ask contextual questions using AI
- Interact with content through a chat-based interface

This project demonstrates a full pipeline from **data extraction → processing → retrieval → AI-based answering (RAG)**.

---

## ✨ Features

- 📄 **Transcript Extraction** from YouTube videos  
- 📝 **Automatic Summarization** using NLP models  
- 💬 **Chat-based Q&A** system  
- 🔍 **Context-aware answers** using RAG (Retrieval-Augmented Generation)  
- 📊 **Lecture stats** (word count, structured data)  
- 🧠 **Chunking + semantic retrieval** for accurate responses  

---

## 🧠 How It Works

1. Extract transcript using YouTube Transcript API  
2. Clean and preprocess the text  
3. Split text into chunks  
4. Convert chunks into embeddings  
5. Store embeddings using FAISS  
6. Retrieve relevant chunks based on user query  
7. Generate answers using a transformer model  

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit  
- **Backend:** FastAPI  
- **NLP Models:** Hugging Face Transformers  
- **Embeddings:** Sentence Transformers  
- **Vector Database:** FAISS  
- **Data Source:** YouTube Transcript API  

---

## 📂 Project Structure

```bash
ak-lecture-assistant/
│
├── app.py                  # Streamlit frontend
├── main.py                 # FastAPI backend
│
├── services/
│   ├── transcript.py       # Transcript extraction
│   ├── rag.py              # Chunking + FAISS logic
│
├── agents/
│   ├── learning.py         # AI summary + Q&A logic
│
├── requirements.txt
└── README.md
