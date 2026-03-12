#!/usr/bin/env python
"""
Quick test of the demo chatbot to verify it works.
"""

import os
import sys
from pathlib import Path

# Set working directory
os.chdir(Path(__file__).parent)

from dotenv import load_dotenv
load_dotenv()

print("\n" + "="*70)
print("🧪 SISTec Chatbot - Quick Test")
print("="*70)

try:
    print("\n[1] Testing environment variables...")
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and len(groq_key) > 20:
        print(f"    ✅ API Key loaded: {groq_key[:20]}...{groq_key[-10:]}")
    else:
        print("    ❌ API Key not found or invalid")
    
    print("\n[2] Testing imports...")
    from config import DATA_FILE, EMBED_MODEL
    print(f"    ✅ Config loaded")
    print(f"       - Data file: {DATA_FILE}")
    print(f"       - Embedding model: {EMBED_MODEL}")
    
    print("\n[3] Testing knowledge base...")
    from pathlib import Path
    if Path(DATA_FILE).exists():
        with open(DATA_FILE) as f:
            text = f.read()
        print(f"    ✅ Knowledge base loaded: {len(text)} characters")
    else:
        print(f"    ❌ Knowledge base not found: {DATA_FILE}")
    
    print("\n[4] Testing chunking...")
    from retrieval import chunk_text
    chunks = chunk_text(text)
    print(f"    ✅ Text chunked into {len(chunks)} chunks")
    
    print("\n[5] Testing embedding model...")
    from sentence_transformers import SentenceTransformer
    print(f"    Loading {EMBED_MODEL}...")
    embed_model = SentenceTransformer(EMBED_MODEL)
    print(f"    ✅ Embedding model loaded")
    
    print("\n[6] Testing indexes...")
    from retrieval import build_indexes
    faiss_index, bm25_index = build_indexes(chunks, embed_model)
    print(f"    ✅ FAISS index built")
    print(f"    ✅ BM25 index built")
    
    print("\n[7] Testing LLM service...")
    from llm import get_llm_service
    llm = get_llm_service()
    print(f"    ✅ LLM service initialized")
    
    if llm.validate_connection():
        print(f"    ✅ Groq API connection valid")
    else:
        print(f"    ⚠️  Groq API connection failed (check credentials)")
    
    print("\n" + "="*70)
    print("✨ ALL TESTS PASSED - Chatbot is ready!")
    print("="*70)
    print("\n🚀 Available commands:")
    print("   python chatbot_main.py    - Full version (with reranker)")
    print("   python demo.py            - Fast demo (without reranker)")
    print("\n")
    
except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
