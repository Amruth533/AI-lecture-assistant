from fastapi import FastAPI
from services.transcript import fetch_transcript
from services.rag import chunk_text, create_vector_store, retrieve
from agents.learning import generate_summary, answer_question

app = FastAPI()

DATA_STORE = {
    "chunks": None,
    "index": None
}


@app.get("/")
def home():
    return {"message": "Backend running 🚀"}


@app.post("/process")
def process_video(url: str):
    try:
        full_text = fetch_transcript(url)

        summary = generate_summary(full_text)

        chunks = chunk_text(full_text)
        index = create_vector_store(chunks)

        DATA_STORE["chunks"] = chunks
        DATA_STORE["index"] = index

        return {
            "summary": summary,
            "full_text": full_text
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/ask")
def ask(question: str):
    try:
        chunks = DATA_STORE["chunks"]
        index = DATA_STORE["index"]

        if not chunks:
            return {"error": "Process a video first"}

        relevant = retrieve(question, index, chunks)

        answer = answer_question(question, relevant)

        return {
            "answer": answer,
            "source": relevant[0]
        }

    except Exception as e:
        return {"error": str(e)}