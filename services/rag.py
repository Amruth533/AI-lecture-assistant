from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")


def chunk_text(text, chunk_size=150):
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]


def create_vector_store(chunks):
    embeddings = model.encode(chunks)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)

    index.add(np.array(embeddings))

    return index


def retrieve(query, index, chunks, k=2):
    query_embedding = model.encode([query])

    distances, indices = index.search(np.array(query_embedding), k)

    return [chunks[i] for i in indices[0]]