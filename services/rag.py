# services/rag.py

"""
AI Lecture Assistant - RAG Engine

Features:
- Transcript chunking
- Semantic embeddings
- FAISS vector retrieval
- Timestamp preservation
- Anti-hallucination filtering
- NO langchain dependency
"""

from sentence_transformers import SentenceTransformer

import faiss
import numpy as np


# ============================================================
# EMBEDDING MODEL
# ============================================================

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


# ============================================================
# SIMPLE TEXT CHUNKER
# ============================================================

def split_text(
    text,
    chunk_size=800,
    overlap=150
):
    """
    Split large text into overlapping chunks.
    """

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# ============================================================
# CHUNK TRANSCRIPT
# ============================================================

def chunk_transcript(
    transcript,
    chunk_size=800,
    overlap=150
):
    """
    Convert transcript into semantic chunks.

    Input:
    [
        {
            "text": "...",
            "start": 12.0,
            "duration": 5.0
        }
    ]

    Output:
    [
        {
            "text": "...",
            "start": 12.0,
            "end": 45.0
        }
    ]
    """

    try:

        if not transcript:

            return []

        # ----------------------------------------------------
        # FULL TEXT
        # ----------------------------------------------------

        full_text = " ".join([
            item["text"]
            for item in transcript
        ])

        text_chunks = split_text(
            full_text,
            chunk_size,
            overlap
        )

        structured_chunks = []

        # ----------------------------------------------------
        # MAP CHUNKS TO TIMESTAMPS
        # ----------------------------------------------------

        for chunk in text_chunks:

            start_time = 0
            end_time = 0

            # Find approximate start timestamp
            for item in transcript:

                if chunk[:40] in item["text"]:

                    start_time = item["start"]

                    break

            # Find approximate end timestamp
            for item in reversed(transcript):

                if chunk[-40:] in item["text"]:

                    end_time = (
                        item["start"]
                        + item["duration"]
                    )

                    break

            structured_chunks.append({
                "text": chunk,
                "start": start_time,
                "end": end_time
            })

        return structured_chunks

    except Exception as e:

        print(f"Chunking Error: {e}")

        return []


# ============================================================
# VECTOR STORE
# ============================================================

def create_vector_store(chunks):
    """
    Create FAISS vector database.
    """

    try:

        if not chunks:

            return None

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = embedding_model.encode(
            texts,
            convert_to_numpy=True
        )

        embeddings = np.array(
            embeddings,
            dtype=np.float32
        )

        dimension = embeddings.shape[1]

        index = faiss.IndexFlatL2(dimension)

        index.add(embeddings)

        return index

    except Exception as e:

        print(f"Vector Store Error: {e}")

        return None


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve(
    query,
    index,
    chunks,
    top_k=4,
    threshold=1.5
):
    """
    Retrieve relevant chunks.

    Anti-hallucination:
    - similarity threshold
    - safe empty retrieval
    """

    try:

        if index is None:

            return []

        # ----------------------------------------------------
        # QUERY EMBEDDING
        # ----------------------------------------------------

        query_embedding = embedding_model.encode(
            [query],
            convert_to_numpy=True
        )

        query_embedding = np.array(
            query_embedding,
            dtype=np.float32
        )

        # ----------------------------------------------------
        # VECTOR SEARCH
        # ----------------------------------------------------

        distances, indices = index.search(
            query_embedding,
            top_k
        )

        retrieved_chunks = []

        # ----------------------------------------------------
        # FILTER RESULTS
        # ----------------------------------------------------

        for score, idx in zip(
            distances[0],
            indices[0]
        ):

            if idx >= len(chunks):

                continue

            # Lower score = better similarity
            if score <= threshold:

                chunk = chunks[idx]

                retrieved_chunks.append({
                    "text": chunk["text"],
                    "start": chunk["start"],
                    "end": chunk["end"],
                    "score": float(score)
                })

        return retrieved_chunks

    except Exception as e:

        print(f"Retrieval Error: {e}")

        return []


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print("Testing rag.py...\n")

    sample_transcript = [
        {
            "text": (
                "Machine learning is a branch "
                "of artificial intelligence."
            ),
            "start": 0,
            "duration": 5
        },
        {
            "text": (
                "Neural networks are inspired "
                "by the human brain."
            ),
            "start": 5,
            "duration": 5
        }
    ]

    # Create chunks
    chunks = chunk_transcript(sample_transcript)

    print("Chunks:")
    print(chunks)

    # Create vector store
    index = create_vector_store(chunks)

    # Retrieve
    results = retrieve(
        "What are neural networks?",
        index,
        chunks
    )

    print("\nRetrieved Results:")
    print(results)