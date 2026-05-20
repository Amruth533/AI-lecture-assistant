# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ============================================================
# IMPORT SERVICES
# ============================================================

from services.transcript import (
    fetch_transcript,
    transcript_to_text
)

from services.rag import (
    chunk_transcript,
    create_vector_store,
    retrieve
)

from agents.learning import (
    generate_summary,
    answer_question
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="AI Lecture Assistant"
)


# ============================================================
# CORS CONFIG
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# GLOBAL STORAGE
# ============================================================

vector_index = None
stored_chunks = None
full_transcript = None


# ============================================================
# REQUEST MODELS
# ============================================================

class VideoRequest(BaseModel):
    url: str


class QuestionRequest(BaseModel):
    question: str


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():

    return {
        "message": "AI Lecture Assistant API Running"
    }


# ============================================================
# PROCESS VIDEO
# ============================================================

@app.post("/process")
def process_video(data: VideoRequest):

    global vector_index
    global stored_chunks
    global full_transcript

    try:

        # ----------------------------------------------------
        # FETCH TRANSCRIPT
        # ----------------------------------------------------

        transcript = fetch_transcript(data.url)

        if not transcript:

            return {
                "error": "Transcript could not be fetched."
            }

        # ----------------------------------------------------
        # FULL TEXT
        # ----------------------------------------------------

        full_text = transcript_to_text(transcript)

        # ----------------------------------------------------
        # CHUNKING
        # ----------------------------------------------------

        chunks = chunk_transcript(transcript)

        if not chunks:

            return {
                "error": "Chunking failed."
            }

        # ----------------------------------------------------
        # VECTOR STORE
        # ----------------------------------------------------

        index = create_vector_store(chunks)

        if index is None:

            return {
                "error": "Vector store creation failed."
            }

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        summary = generate_summary(full_text)

        # ----------------------------------------------------
        # STORE GLOBALLY
        # ----------------------------------------------------

        vector_index = index
        stored_chunks = chunks
        full_transcript = full_text

        # ----------------------------------------------------
        # RETURN RESPONSE
        # ----------------------------------------------------

        return {
            "summary": summary,
            "transcript": full_text[:5000],
            "stats": {
                "word_count": len(full_text.split()),
                "chunk_count": len(chunks)
            }
        }

    except Exception as e:

        return {
            "error": f"Processing failed: {str(e)}"
        }


# ============================================================
# ASK QUESTION
# ============================================================

@app.post("/ask")
def ask_question_endpoint(data: QuestionRequest):

    global vector_index
    global stored_chunks

    try:

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if vector_index is None:

            return {
                "error": (
                    "Please process a lecture first."
                )
            }

        # ----------------------------------------------------
        # RETRIEVE CHUNKS
        # ----------------------------------------------------

        retrieved_chunks = retrieve(
            query=data.question,
            index=vector_index,
            chunks=stored_chunks
        )

        # ----------------------------------------------------
        # GENERATE ANSWER
        # ----------------------------------------------------

        result = answer_question(
            question=data.question,
            retrieved_chunks=retrieved_chunks
        )

        return result

    except Exception as e:

        return {
            "error": f"Question answering failed: {str(e)}"
        }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print("main.py loaded successfully")