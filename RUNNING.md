# Quick Start Guide - Refactored SISTec Chatbot

## 🚀 Running the Chatbot

### Option 1: Run the Professional Refactored Version (Recommended)
```bash
python chatbot_main.py
```

This is the production-ready version with:
- ✅ Full modular architecture
- ✅ Comprehensive error handling
- ✅ Professional logging
- ✅ Better UX and commands
- ✅ Type safety throughout
- ✅ Cross-platform support

### Option 2: Run the Original Version
```bash
python chatbot.py
```

This is the original implementation (kept for reference).

---

## 📋 Prerequisites

1. **Python 3.8+**
   ```bash
   python --version
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note**: On Windows, you may need to also install:
   ```bash
   pip install pyaudio
   ```
   
   **Problem with PyAudio?** See [Troubleshooting](#troubleshooting)

3. **Get Groq API Key**
   - Visit: https://console.groq.com/keys
   - Create a new API key
   - Copy the key

4. **Configure .env file**
   ```bash
   # Edit .env file and add:
   GROQ_API_KEY=your_api_key_here
   ```

---

## 🎮 Using the Chatbot

### Welcome Screen
```
============================================================
🎓 SAGAR GROUP OF INSTITUTIONS (SGI) - AI Chatbot
Powered by RAG + LLM + Voice Technology
============================================================

📚 Commands:
  <question>      - Ask a text question
  voice [N]       - Record voice input (N seconds, default=5)
  history         - Show conversation history
  help            - Show this help message
  exit            - Exit chatbot
```

### Example Interactions

#### Ask via Text
```
📝 You: What are the departments in SGI?

⏳ Thinking...

🤖 Bot: SGI offers Engineering, Pharmacy, and Management programs across multiple campuses...
```

#### Ask via Voice
```
📝 You: voice 10

🎙️ Listening (10s)...
🗣️ Recognized: "Tell me about student life at SGI"

⏳ Thinking...

🤖 Bot: SGI provides vibrant campus life with various clubs, sports facilities, and cultural events...
```

#### View Conversation History
```
📝 You: history

📋 Conversation History:
------------------------------------------------------------

[1] Q: What are the departments in SGI?
    A: SGI offers Engineering, Pharmacy, and Management programs...
    Chunks used: 3

[2] Q: Tell me about student life at SGI
    A: SGI provides vibrant campus life with various clubs...
    Chunks used: 2

------------------------------------------------------------
```

---

## 📁 Project Structure

### Refactored Code (New)
```
sistec_chatbot/
├── config.py              # Configuration management
├── utils.py               # Utility functions & validation
├── retrieval.py           # RAG implementation (SentenceTransformer + FAISS + BM25)
├── llm.py                 # LLM service (Groq API wrapper)
├── voice.py               # Voice I/O (speech recognition + TTS)
├── chatbot_main.py        # Main application (Recommended!)
└── chatbot.log            # Application logs
```

### Knowledge Base & Config
```
├── sistec_rag_data.md     # Knowledge base file
├── .env                   # API keys and config (NEVER commit!)
├── .gitignore            # Files to ignore in Git
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

### Original Code (Legacy)
```
├── chatbot.py            # Original implementation (kept for reference)
└── IMPROVEMENTS.md       # Detailed improvement documentation
```

---

## 🔧 Configuration

### Environment Variables

Create or edit `.env` file:

```bash
# Required
GROQ_API_KEY=gsk_...                    # Get from https://console.groq.com/keys

# Optional - Groq Model (default: llama-3.3-70b-versatile)
GROQ_MODEL=llama-3.3-70b-versatile

# Optional - Processing parameters
CHUNK_SIZE=800                          # Document chunk size
CHUNK_OVERLAP=150                       # Overlap between chunks
ALPHA=0.5                               # BM25/FAISS weight balance

# Optional - Retrieval tuning
BM25_TOP_K=10                           # BM25 candidates to retrieve
FAISS_TOP_K=10                          # FAISS candidates to retrieve
RERANK_TOP_K=5                          # Final results to show

# Optional - Features
ENABLE_VOICE_OUTPUT=true                # Play responses as speech
LOG_LEVEL=INFO                          # DEBUG, INFO, WARNING, ERROR
```

---

## 📊 How It Works

### Architecture

```
User Input
    ↓
[Voice Input (optional) / Text Input]
    ↓
[Chunked Knowledge Base]
    ↓
[Hybrid Retrieval]
├─ BM25 Keyword Search
└─ FAISS Vector Search
    ↓
[Reciprocal Rank Fusion]
    ↓
[CrossEncoder Reranking]
    ↓
[Context + Query] → [Groq LLM]
    ↓
[Generated Response]
    ↓
[Display] + [Voice Output (optional)]
```

### Retrieval Process

1. **BM25 Search** (Keyword-based)
   - Retrieves top 10 keyword-matching chunks
   - Fast, traditional IR approach

2. **FAISS Search** (Semantic)
   - Converts query to embedding
   - Finds top 10 semantically similar chunks
   - Uses BAAI/bge-base-en-v1.5 model

3. **Reciprocal Rank Fusion (RRF)**
   - Combines BM25 and FAISS scores
   - ALPHA parameter controls weighting
   - Creates unified candidate list

4. **CrossEncoder Reranking**
   - Uses ms-marco-MiniLM-L-6-v2 model
   - Re-scores all candidates
   - Returns top 5 most relevant

5. **LLM Generation**
   - Groq's llama-3.3-70b-versatile model
   - Temperature = 0.3 (deterministic responses)
   - Context-aware answer generation

---

## 📝 Logging

All events are logged to `chatbot.log`:

```
2026-03-12 21:20:30,048 - chatbot_main - INFO - Initializing SISTec Chatbot...
2026-03-12 21:20:31,869 - retrieval - INFO - Building indexes for 42 chunks...
2026-03-12 21:20:45,123 - llm - INFO - Generating response for: What are the departments?...
```

**View logs in real-time:**
```bash
tail -f chatbot.log
```

---

## 🐛 Troubleshooting

### Issue: "GROQ_API_KEY not found"
**Solution:**
1. Open `.env` file
2. Add: `GROQ_API_KEY=your_actual_key_here`
3. Save and restart chatbot

### Issue: "ModuleNotFoundError: No module named 'X'"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Voice input not working
**Possible Solutions:**
1. **Missing PyAudio:**
   ```bash
   pip install pyaudio
   ```
   
   Or on macOS:
   ```bash
   brew install portaudio
   pip install pyaudio
   ```

2. **Microphone permission (macOS/Linux):**
   - Check system settings for microphone access

3. **No microphone detected:**
   - Use text mode: just type questions instead of `voice`

### Issue: Voice output (TTS) not playing
**Solution:**
- Text-to-speech may be disabled or fail silently
- The .mp3 file is still created in `response.mp3`
- Use `ENABLE_VOICE_OUTPUT=false` in .env to disable

### Issue: Models downloading very slowly
**Solution:**
- First run downloads ~200MB of models
- Subsequent runs use cached models
- Network may be slow - wait patiently ☕

### Issue: "FAISS" error or crashes
**Solution:**
```bash
# Reinstall FAISS
pip uninstall faiss-cpu
pip install faiss-cpu
```

---

## 🎯 Performance Tips

1. **First Run**: Slower (downloads models) ⏳
   - Embedding model: ~128 MB
   - Reranker model: ~65 MB
   - Subsequent runs are much faster ⚡

2. **Voice Input**: Takes longer than text
   - Network latency for Google Speech Recognition
   - Type questions for faster interaction

3. **Large Knowledge Base**:
   - FAISS is RAM-intensive
   - May need 4GB+ RAM for very large bases
   - Chunk size affects both quality and speed

4. **Groq API Rate Limiting**:
   - Free tier has limits
   - Wait between requests if rate-limited
   - Consider upgrading for production use

---

## 🔐 Security Notes

⚠️ **IMPORTANT:**
- Never commit `.env` file to Git ✅ (Already in .gitignore)
- API keys are sensitive - treat like passwords
- Don't share your API key with others
- Rotate keys periodically for production

---

## 📚 Understanding Components

### config.py
- Centralized configuration
- Environment variable management
- Type-safe configuration object

### utils.py
- Logging setup
- Input validation functions
- Custom exceptions
- Helper functions

### retrieval.py
- RAGRetriever class
- Hybrid search implementation
- Index building
- Reranking logic

### llm.py
- LLMService class
- Groq API interaction
- Prompt management
- Response generation

### voice.py
- VoiceProcessor class
- Speech recognition
- Text-to-speech
- Cross-platform audio playback

### chatbot_main.py
- SISTecChatbot main class
- Interactive session loop
- Command handling
- State management

---

## 🚀 Next Steps

1. **Explore the code:**
   - Check docstrings: `python -c "import retrieval; help(retrieval.RAGRetriever)"`
   - Review IMPROVEMENTS.md for detailed changes

2. **Customize:**
   - Edit `config.py` to tune parameters
   - Modify `sistec_rag_data.md` to update knowledge base
   - Update `.env` with your settings

3. **Integrate:**
   - Import classes in your own projects
   - Use as library: `from chatbot_main import SISTecChatbot`
   - Build web interfaces on top

4. **Develop:**
   - Add unit tests (pytest)
   - Create web API (FastAPI)
   - Deploy to cloud (AWS, GCP, Azure)

---

## 📞 Support

- Check IMPROVEMENTS.md for technical details
- Review code docstrings for function documentation
- Check chatbot.log for error messages
- Visit https://console.groq.com for API issues

---

## 📄 File Reference

| File | Purpose | Refactored |
|------|---------|-----------|
| chatbot_main.py | Main application ✅ **USE THIS** | ✅ Yes |
| chatbot.py | Original version (legacy) | ❌ No |
| config.py | Configuration management | ✅ New |
| utils.py | Utilities & validation | ✅ New |
| retrieval.py | RAG implementation | ✅ New |
| llm.py | LLM service | ✅ New |
| voice.py | Voice processing | ✅ New |
| sistec_rag_data.md | Knowledge base | ❌ Original |
| requirements.txt | Dependencies | ✅ Updated |
| .env | API key config | ✅ Essential |
| .gitignore | Git rules | ✅ New |
| IMPROVEMENTS.md | Detailed changes | ✅ New |
| README.md | Full documentation | ✅ Updated |
| RUNNING.md | This file | ✅ New |

---

**Happy chatting with SGI Chatbot! 🎓🤖**
