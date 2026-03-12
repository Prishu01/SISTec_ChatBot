# SISTec RAG Chatbot - Professional Voice Edition

An intelligent, production-grade conversational AI system for SISTec (Sagar Group of Institutions) using Retrieval Augmented Generation (RAG), advanced voice I/O, and sophisticated hybrid search algorithms.

## Features

- **Hybrid Retrieval**: Combines BM25 and FAISS vector search for comprehensive context retrieval
- **Reranking**: Uses CrossEncoder to rank retrieved contexts by relevance
- **Voice Input**: Convert speech to text using Google Speech Recognition
- **Voice Output**: AI responses are converted to speech using Google Text-to-Speech
- **RAG Architecture**: Answers questions based on knowledge base (sistec_rag_data.md)
- **Advanced NLP**: Powered by SentenceTransformers and Groq's LLM API

## Prerequisites

- Python 3.8+
- Groq API key (free tier available at https://console.groq.com)
- Microphone for voice input

## Installation

1. **Clone or navigate to the project folder**
   ```bash
   cd sistec_chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Groq API Key**
   - Go to https://console.groq.com/keys
   - Generate a new API key
   - Open `.env` file and add your key:
     ```
     GROQ_API_KEY=your_api_key_here
     ```
   - Save the file

## Usage

**Start the chatbot:**
```bash
python chatbot.py
```

**Interactive Commands:**
- `type your question` - Ask a question via text
- `voice` - Record a 5-second voice message
- `voice 10` - Record a 10-second voice message (adjust duration as needed)
- `exit` - Quit the chatbot

## Example Interactions

```
You: What are the main features of SISTec?
Bot: [Responds with relevant information from knowledge base]

You: voice
🎙️ Speak now (5 sec)...
Bot: [Converts your speech to text and responds with audio output]
```

## Project Structure

```
sistec_chatbot/
├── chatbot.py                  # Main chatbot application
├── sistec_rag_data.md          # Knowledge base
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (your API key)
├── .gitignore                  # Git ignore rules
└── response.mp3                # Generated audio responses
```

## Architecture Details

### 1. **Indexing Phase**
- Loads knowledge base from `sistec_rag_data.md`
- Splits text into chunks (800 chars with 150 char overlap)
- Creates embeddings using `BAAI/bge-base-en-v1.5` model
- Builds FAISS vector index for semantic search
- Builds BM25 index for keyword-based search

### 2. **Retrieval Phase**
- **BM25 Search**: Keyword-based relevance (Top 10)
- **FAISS Search**: Vector similarity search (Top 10)
- **Reciprocal Rank Fusion (RRF)**: Combines both methods with configurable weights (α=0.5)

### 3. **Reranking Phase**
- Uses `cross-encoder/ms-marco-MiniLM-L-6-v2` to score combined results
- Returns top 5 most relevant contexts

### 4. **LLM Generation Phase**
- Uses Groq's `llama-3.3-70b-versatile` model
- Augments prompt with retrieved context
- Generates concise answers (2-4 sentences)

### 5. **Voice Processing**
- **Input**: Google Speech Recognition API
- **Output**: Google Text-to-Speech (gTTS) saved as MP3

## Configuration

Edit these variables in `chatbot.py` to customize behavior:

```python
CHUNK_SIZE = 800              # Text chunk size for splitting
CHUNK_OVERLAP = 150           # Overlap between chunks
BM25_TOP_K = 10               # BM25 results to retrieve
FAISS_TOP_K = 10              # FAISS results to retrieve
RERANK_TOP_K = 5              # Final reranked results
ALPHA = 0.5                   # BM25 weight (1-ALPHA = FAISS weight)
GROQ_MODEL = "llama-3.3-70b-versatile"  # LLM model to use
```

## Troubleshooting

### "GROQ_API_KEY not found"
- Ensure `.env` file exists in the project folder
- Check that `GROQ_API_KEY=` is set to your actual API key
- Restart the chatbot

### Voice Input Not Working
- Ensure your microphone is properly connected
- Check microphone permissions in system settings
- Try `voice` command with a longer duration: `voice 10`

### Slow Performance
- First run takes longer (downloads ML models)
- Subsequent runs are much faster
- FAISS indexing is RAM-intensive for large knowledge bases

### Models Not Downloading
- First run automatically downloads:
  - BAAI/bge-base-en-v1.5 (~128 MB)
  - cross-encoder/ms-marco-MiniLM-L-6-v2 (~65 MB)
- Ensure stable internet connection during first run

## Dependencies

- **LLM**: groq
- **Embeddings**: sentence-transformers
- **Vector DB**: faiss-cpu
- **Text Processing**: langchain-text-splitters, rank_bm25
- **Speech**: SpeechRecognition, pyaudio, gtts
- **Utilities**: python-dotenv, numpy

## API Pricing

- **Groq**: Free tier available (rate-limited)
- **Google Speech Recognition**: Free (via SpeechRecognition library)
- **Google TTS**: Free (via gTTS library)

## Limitations

- Groq free tier has rate limits
- Voice output plays on Windows via `start` command (modify for other OS)
- Microphone required for voice input
- Knowledge base limited to contents of `sistec_rag_data.md`

## Future Enhancements

- [ ] Multi-language support
- [ ] Persistent conversation history
- [ ] Custom knowledge base upload
- [ ] Web interface
- [ ] Database integration
- [ ] Model selection dropdown
- [ ] Advanced voice settings
- [ ] Conversation analytics

## License

This project is created for educational purposes at SISTec.

## Support

For issues or questions, check the troubleshooting section or review the inline code comments.

---

**Happy chatting with SISTec Bot!** 🎓🤖
