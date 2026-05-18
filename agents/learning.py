from transformers import pipeline

# Only supported task
generator = pipeline("text-generation", model="gpt2")


def generate_summary(text):
    prompt = f"Summarize this lecture:\n{text[:500]}"

    result = generator(prompt, max_length=150, num_return_sequences=1)

    summary = result[0]["generated_text"].replace(prompt, "").strip()

    return summary


def answer_question(question, context_chunks):
    context = " ".join(context_chunks[:2])

    prompt = f"""
    Context: {context}

    Question: {question}

    Answer:
    """

    result = generator(prompt, max_length=200, num_return_sequences=1)

    answer = result[0]["generated_text"].split("Answer:")[-1].strip()

    return answer