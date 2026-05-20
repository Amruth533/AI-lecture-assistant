# agents/learning.py

"""
AI Lecture Assistant - Learning Module

Features:
- Lecture summarization
- Grounded Q&A
- Hallucination control
- Ollama integration
- Timestamp-aware responses
"""

import requests


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an AI Lecture Assistant.

STRICT RULES:
1. Answer ONLY from the provided lecture context.
2. NEVER use outside knowledge.
3. NEVER hallucinate or guess.
4. If answer is missing from context, say:
   "This topic was not clearly covered in the lecture."
5. Keep answers concise and accurate.
6. Reference timestamps if available.
"""


# ============================================================
# OLLAMA CONFIG
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"

OLLAMA_MODEL = "mistral"


# ============================================================
# OLLAMA REQUEST FUNCTION
# ============================================================

def ask_ollama(prompt: str) -> str:
    """
    Send prompt to local Ollama model.
    """

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "response",
            "No response generated."
        )

    except requests.exceptions.ConnectionError:

        return (
            "ERROR: Ollama is not running.\n\n"
            "Run this command in terminal:\n"
            "ollama run mistral"
        )

    except Exception as e:

        return f"LLM Error: {str(e)}"


# ============================================================
# SUMMARY GENERATION
# ============================================================

def generate_summary(text: str) -> str:
    """
    Generate bullet-point lecture summary.
    """

    try:

        if not text:

            return "No transcript available."

        # Prevent overly large prompts
        text = text[:5000]

        prompt = f"""
Summarize the following lecture into concise bullet points.

Lecture Transcript:
{text}

IMPORTANT:
- Return ONLY bullet points
- Keep summary concise
- Focus on major concepts
"""

        response = ask_ollama(prompt)

        return response

    except Exception as e:

        return f"Summary generation failed: {str(e)}"


# ============================================================
# QUESTION ANSWERING
# ============================================================

def answer_question(
    question: str,
    retrieved_chunks: list
):
    """
    Answer questions using retrieved transcript chunks only.
    """

    try:

        # ----------------------------------------------------
        # EMPTY RETRIEVAL CHECK
        # ----------------------------------------------------

        if not retrieved_chunks:

            return {
                "answer": (
                    "This topic was not clearly "
                    "covered in the lecture."
                ),
                "sources": []
            }

        # ----------------------------------------------------
        # BUILD CONTEXT
        # ----------------------------------------------------

        context_list = []

        for chunk in retrieved_chunks:

            timestamp = round(
                chunk.get("start", 0) / 60,
                2
            )

            text = chunk.get("text", "")

            context_list.append(
                f"""
Timestamp: {timestamp} minutes

Lecture Context:
{text}
"""
            )

        context = "\n\n".join(context_list)

        # ----------------------------------------------------
        # FINAL PROMPT
        # ----------------------------------------------------

        prompt = f"""
{SYSTEM_PROMPT}

========================================
LECTURE CONTEXT
========================================

{context}

========================================
QUESTION
========================================

{question}

========================================
ANSWER
========================================

Answer ONLY from the lecture context.
"""

        # ----------------------------------------------------
        # GET RESPONSE
        # ----------------------------------------------------

        response = ask_ollama(prompt)

        # ----------------------------------------------------
        # EXTRA HALLUCINATION FILTER
        # ----------------------------------------------------

        hallucination_phrases = [
            "generally speaking",
            "typically",
            "usually",
            "in general",
            "commonly",
            "most likely"
        ]

        lower_response = response.lower()

        for phrase in hallucination_phrases:

            if phrase in lower_response:

                response = (
                    "The lecture does not clearly "
                    "provide enough information "
                    "to answer this confidently."
                )

                break

        # ----------------------------------------------------
        # RETURN RESULT
        # ----------------------------------------------------

        return {
            "answer": response,
            "sources": retrieved_chunks
        }

    except Exception as e:

        return {
            "answer": f"Question answering failed: {str(e)}",
            "sources": []
        }


# ============================================================
# LOCAL TESTING
# ============================================================

if __name__ == "__main__":

    print("Testing learning.py...\n")

    test_response = ask_ollama(
        "Say hello in one short sentence."
    )

    print(test_response)