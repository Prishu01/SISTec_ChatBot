import numpy as np
import os
import speech_recognition as sr
from gtts import gTTS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
import faiss
from groq import Groq


# -----------------------------
# CONFIGURATION
# -----------------------------

DATA_FILE = "sistec_rag_data.md"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

EMBED_MODEL = "BAAI/bge-base-en-v1.5"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

BM25_TOP_K = 10
FAISS_TOP_K = 10
RERANK_TOP_K = 5

ALPHA = 0.5

AUDIO_FILE = "response.mp3"


# -----------------------------
# BUILD INDEXES
# -----------------------------

def build_indexes(filepath):

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    print(f"📄 File loaded — {len(text)} characters")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunks = splitter.split_text(text)

    print(f" Chunks created: {len(chunks)}")

    print(" Loading embedding model...")
    embed_model = SentenceTransformer(EMBED_MODEL)

    embeddings = embed_model.encode(chunks, show_progress_bar=True)

    print(" Building FAISS index...")
    faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
    faiss_index.add(np.array(embeddings))

    print(" Building BM25 index...")
    bm25_index = BM25Okapi([chunk.lower().split() for chunk in chunks])

    print(" Loading reranker...")
    reranker = CrossEncoder(RERANK_MODEL)

    print(" All indexes ready!\n")

    return chunks, faiss_index, bm25_index, embed_model, reranker


# -----------------------------
# HYBRID RETRIEVAL
# -----------------------------

def hybrid_retrieve(query, chunks, faiss_index, bm25_index, embed_model):

    bm25_scores = bm25_index.get_scores(query.lower().split())
    bm25_top_idx = np.argsort(bm25_scores)[::-1][:BM25_TOP_K]

    query_embedding = embed_model.encode([query])

    _, faiss_top_idx = faiss_index.search(
        np.array(query_embedding),
        FAISS_TOP_K
    )

    faiss_top_idx = faiss_top_idx[0]

    rrf_scores = {}

    for rank, idx in enumerate(bm25_top_idx):
        rrf_scores[idx] = rrf_scores.get(idx, 0) + (1 - ALPHA) / (rank + 1)

    for rank, idx in enumerate(faiss_top_idx):
        rrf_scores[idx] = rrf_scores.get(idx, 0) + ALPHA / (rank + 1)

    sorted_idx = sorted(rrf_scores, key=rrf_scores.get, reverse=True)

    return [chunks[i] for i in sorted_idx]


# -----------------------------
# RERANK
# -----------------------------

def retrieve(query, chunks, faiss_index, bm25_index, embed_model, reranker):

    candidates = hybrid_retrieve(
        query,
        chunks,
        faiss_index,
        bm25_index,
        embed_model
    )

    scores = reranker.predict([[query, c] for c in candidates])

    ranked = sorted(zip(scores, candidates), reverse=True)

    return "\n\n".join([c for _, c in ranked[:RERANK_TOP_K]])


# -----------------------------
# VOICE INPUT
# -----------------------------

def record_voice(duration=5):

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print(f"🎙️ Speak now ({duration} sec)...")

        recognizer.adjust_for_ambient_noise(source)

        audio = recognizer.listen(
            source,
            phrase_time_limit=duration
        )

    try:

        text = recognizer.recognize_google(audio)

        print(f'🗣️ You said: "{text}"')

        return text

    except sr.UnknownValueError:

        print(" Could not understand audio")

        return ""

    except sr.RequestError:

        print(" Speech service error")

        return ""


# -----------------------------
# VOICE OUTPUT
# -----------------------------

def speak(text):

    tts = gTTS(text=text, lang="en")

    tts.save(AUDIO_FILE)

    # Windows
    os.system(f"start {AUDIO_FILE}")


# -----------------------------
# ASK LLM
# -----------------------------

def ask(question,
        chunks,
        faiss_index,
        bm25_index,
        embed_model,
        reranker,
        groq_client):

    context = retrieve(
        question,
        chunks,
        faiss_index,
        bm25_index,
        embed_model,
        reranker
    )

    prompt = f"""
You are a helpful AI assistant for SISTec (Sagar Institute of Science & Technology), Bhopal.

Answer ONLY using the context below.
Keep answers short (2-4 sentences).

If the answer is not present, say:
"I don't have that information."

Context:
{context}

Question: {question}

Answer:
"""

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# -----------------------------
# CHAT LOOP
# -----------------------------

def chat_loop(
        chunks,
        faiss_index,
        bm25_index,
        embed_model,
        reranker,
        groq_client
):

    print("\n" + "="*50)
    print("🎓 SISTec Voice Chatbot")
    print("Hybrid Search + Voice + RAG")
    print("="*50)

    print("""
Commands:

type question → text input
voice         → speak 5 seconds
voice 10      → speak 10 seconds
exit          → quit
""")

    while True:

        user_input = input("You: ").strip()

        if user_input == "":
            continue

        if user_input.lower() == "exit":

            speak("Goodbye. Have a great day.")

            print("Bot: Goodbye!")

            break

        if user_input.lower().startswith("voice"):

            parts = user_input.split()

            duration = 5

            if len(parts) > 1 and parts[1].isdigit():
                duration = int(parts[1])

            question = record_voice(duration)

            if question == "":
                continue

        else:

            question = user_input

        print("🤔 Thinking...")

        answer = ask(
            question,
            chunks,
            faiss_index,
            bm25_index,
            embed_model,
            reranker,
            groq_client
        )

        print("\nBot:", answer, "\n")

        speak(answer)


# -----------------------------
# MAIN
# -----------------------------

def main():

    if GROQ_API_KEY is None:
        print("❌ GROQ_API_KEY not found!")
        print("\n📋 Setup Instructions:")
        print("1. Get your API key from: https://console.groq.com/keys")
        print("2. Add it to .env file: GROQ_API_KEY=your_key_here")
        print("3. Save and try again\n")
        return

    chunks, faiss_index, bm25_index, embed_model, reranker = build_indexes(DATA_FILE)

    groq_client = Groq(api_key=GROQ_API_KEY)

    chat_loop(
        chunks,
        faiss_index,
        bm25_index,
        embed_model,
        reranker,
        groq_client
    )


if __name__ == "__main__":
    main()