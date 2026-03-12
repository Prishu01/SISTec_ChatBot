# SISTec Chatbot - File Reference Guide

Complete documentation of all files created during the professional refactoring.

---

## 📂 Directory Structure

```
sistec_chatbot/
│
├── 🎯 MAIN APPLICATION (Use chatbot_main.py!)
│   ├── chatbot_main.py              ⭐ Professional refactored version
│   └── chatbot.py                   🏛️ Original version (legacy)
│
├── ⚙️ CORE MODULES (New - Modular Design)
│   ├── config.py                    Configuration management
│   ├── utils.py                     Utilities & validation
│   ├── retrieval.py                 RAG implementation
│   ├── llm.py                       LLM service integration
│   └── voice.py                     Voice I/O processing
│
├── 📚 DATA & CONFIG
│   ├── sistec_rag_data.md           Knowledge base
│   ├── .env                         API keys & secrets
│   └── .gitignore                   Git ignore rules
│
├── 📖 DOCUMENTATION
│   ├── README.md                    Full documentation
│   ├── RUNNING.md                   Quick start guide
│   ├── PROFESSIONAL_SUMMARY.md      This summary
│   ├── IMPROVEMENTS.md              Detailed improvements
│   ├── FILES.md                     This document
│   └── EXAMPLES.py                  Usage examples & tests
│
├── 📋 DEPENDENCIES
│   └── requirements.txt             Package requirements
│
└── 📊 LOGS
    ├── chatbot.log                  Application logs
    └── .cache/                      Cache directory
```

---

## 📄 File Details

### **APPLICATION ENTRY POINTS**

#### `chatbot_main.py` ⭐ **START HERE**
- **Purpose**: Main application entry point
- **Type**: Python module + executable
- **Key Class**: `SISTecChatbot`
- **What It Does**:
  - Orchestrates RAG, LLM, and voice components
  - Manages interactive chat sessions
  - Tracks conversation history
  - Handles user commands
- **How to Use**:
  ```bash
  python chatbot_main.py
  ```
- **Size**: ~250 lines
- **Status**: ✅ Production-ready

#### `chatbot.py` 🏛️ **Legacy**
- **Purpose**: Original implementation
- **Type**: Python module (can still be executed)
- **What It Does**: Same as before (monolithic approach)
- **How to Use**:
  ```bash
  python chatbot.py
  ```
- **Size**: ~350 lines
- **Status**: ❌ Legacy (kept for reference)

---

### **CORE MODULES (Professional Implementation)**

#### **1. `config.py`** - Configuration Management
- **Purpose**: Centralized configuration
- **Key Features**:
  - Environment variable support
  - Type-safe settings
  - Sensible defaults
  - Path management
- **What You Can Customize**:
  - GROQ_MODEL
  - CHUNK_SIZE, CHUNK_OVERLAP
  - BM25_TOP_K, FAISS_TOP_K, RERANK_TOP_K
  - ALPHA (BM25/FAISS weight)
  - LOG_LEVEL
  - ENABLE_VOICE_OUTPUT
- **Size**: ~80 lines
- **Key Variables**: 30+
- **Status**: ✅ Refactored

---

#### **2. `utils.py`** - Utilities & Validation
- **Purpose**: Common utilities and helper functions
- **Key Classes**:
  - `ConfigError` - Configuration exception
  - `ValidationError` - Validation exception
- **Key Functions**:
  - `setup_logger()` - Configure logging system
  - `validate_api_key()` - Validate API key format
  - `validate_file_exists()` - Check file existence
  - `validate_duration()` - Validate recording duration
  - `sanitize_text()` - Clean and truncate text
  - `get_platform_info()` - Detect OS
  - `format_duration()` - Format seconds to readable text
- **Size**: ~150 lines
- **Functions**: 7+
- **Status**: ✅ New

---

#### **3. `retrieval.py`** - RAG Implementation
- **Purpose**: Handles document retrieval and reranking
- **Key Class**: `RAGRetriever`
- **What It Does**:
  1. Loads and chunks documents
  2. Builds FAISS vector index
  3. Builds BM25 keyword index
  4. Performs hybrid retrieval
  5. Reranks results with CrossEncoder
- **Key Methods**:
  - `__init__()` - Initialize with chunks
  - `set_indexes()` - Set FAISS and BM25 indexes
  - `hybrid_retrieve()` - BM25 + FAISS search
  - `retrieve()` - Full pipeline with reranking
- **Key Functions**:
  - `build_indexes()` - Build FAISS and BM25 indexes
  - `chunk_text()` - Split text into chunks
- **Size**: ~250 lines
- **Methods**: 6+
- **Status**: ✅ Refactored (from monolithic code)

---

#### **4. `llm.py`** - LLM Service Integration
- **Purpose**: Interact with Groq LLM API
- **Key Class**: `LLMService`
- **What It Does**:
  1. Manages Groq API connection
  2. Handles prompt construction
  3. Validates inputs
  4. Manages error handling
  5. Tunes model parameters
- **Key Methods**:
  - `__init__()` - Initialize with API key validation
  - `generate_response()` - Generate LLM response
  - `validate_connection()` - Test API connectivity
  - `_build_prompt()` - Construct prompt
- **System Prompt**: Customizable, professional tone
- **Temperature**: 0.3 (low for consistency)
- **Max Tokens**: 500
- **Size**: ~200 lines
- **Status**: ✅ Refactored (with error handling)

---

#### **5. `voice.py`** - Voice Processing
- **Purpose**: Handle speech-to-text and text-to-speech
- **Key Class**: `VoiceProcessor`
- **Platforms Supported**:
  - ✅ Windows (`os.startfile()`)
  - ✅ macOS (`afplay`)
  - ✅ Linux (`aplay`/`paplay`)
- **Key Methods**:
  - `record_voice()` - Record audio and convert to text
  - `text_to_speech()` - Convert text to speech
  - `_recognize_with_fallback()` - Try multiple recognition engines
  - `_play_audio()` - Play audio file (cross-platform)
- **Key Functions**:
  - `get_voice_processor()` - Factory function
- **Size**: ~280 lines
- **Status**: ✅ Refactored (cross-platform, robust)

---

### **DATA & CONFIGURATION FILES**

#### **`sistec_rag_data.md`** - Knowledge Base
- **Purpose**: Source material for RAG system
- **Format**: Markdown with structured sections
- **Content**: Information about SGI institution
- **Size**: ~1-2 KB (expandable)
- **Chunks Created**: ~10-20 (depends on content)
- **Status**: ✅ Original (can be expanded)

#### **`.env`** - Environment Variables
- **Purpose**: Store sensitive configuration
- **Format**: KEY=VALUE (one per line)
- **What to Store**:
  ```
  GROQ_API_KEY=your_api_key_here
  GROQ_MODEL=llama-3.3-70b-versatile
  LOG_LEVEL=INFO
  ENABLE_VOICE_OUTPUT=true
  ```
- **Security**: ⚠️ NEVER commit this file!
- **Location**: Project root
- **Status**: ✅ Essential

#### **`.gitignore`** - Git Ignore Rules
- **Purpose**: Tell Git which files to ignore
- **Include**:
  - `.env` (API keys!)
  - `__pycache__/` (Python cache)
  - `*.mp3` (audio files)
  - `chatbot.log` (logs)
  - `.cache/` (cached models)
- **Status**: ✅ New

---

### **DOCUMENTATION FILES**

#### **`README.md`** - Full Documentation
- **Content**:
  - Feature overview
  - Installation instructions
  - Usage guide
  - Architecture explanation
  - Configuration options
  - Troubleshooting
  - Dependencies list
- **Audience**: Everyone
- **Size**: ~400 lines
- **Status**: ✅ Updated

#### **`RUNNING.md`** - Quick Start Guide
- **Content**:
  - How to run the chatbot
  - Prerequisites
  - Configuration
  - Example interactions
  - Interactive commands
  - Troubleshooting
  - Performance tips
- **Audience**: Users wanting to get started quickly
- **Size**: ~300 lines
- **Status**: ✅ New

#### **`IMPROVEMENTS.md`** - Technical Deep Dive
- **Content**:
  - Before/after code comparisons
  - Architecture improvements
  - Error handling explanations
  - Type hints demonstration
  - Configuration management details
  - Voice processing improvements
  - Code quality metrics
  - Future enhancement suggestions
- **Audience**: Developers studying the refactoring
- **Size**: ~600 lines
- **Status**: ✅ New

#### **`PROFESSIONAL_SUMMARY.md`** - Executive Summary
- **Content**:
  - High-level improvements
  - Code quality checklist
  - Metrics and statistics
  - File structure overview
  - Learning value
  - Migration path
  - Next steps
- **Audience**: Project managers and architects
- **Size**: ~400 lines
- **Status**: ✅ New

#### **`FILES.md`** - This Document
- **Content**: Complete file reference guide
- **Purpose**: Navigation and understanding structure
- **Audience**: Anyone looking at the codebase
- **Status**: ✅ New

#### **`EXAMPLES.py`** - Usage Examples & Tests
- **Content**:
  - 14+ example use cases
  - Integration patterns
  - Test examples
  - Benchmark code
  - Unit test functions
  - Batch processing examples
  - Performance testing
- **How to Use**:
  ```bash
  python EXAMPLES.py
  ```
- **Size**: ~500 lines
- **Examples**: 14+
- **Status**: ✅ New

---

### **DEPENDENCY FILE**

#### **`requirements.txt`** - Python Dependencies
- **Purpose**: List all required packages
- **Format**: One package per line with version constraints
- **Core Packages**:
  - `groq` - Groq API client
  - `sentence-transformers` - Embedding models
  - `faiss-cpu` - Vector search
  - `rank-bm25` - BM25 ranking
  - `langchain-text-splitters` - Text chunking
  - `gtts` - Text-to-speech
  - `SpeechRecognition` - Speech-to-text
  - `pyaudio` - Audio device interface
  - `python-dotenv` - Environment variables
  - `numpy` - Numerical computing
- **Installation**:
  ```bash
  pip install -r requirements.txt
  ```
- **Size**: ~20 lines
- **Status**: ✅ Updated

---

## 📊 File Statistics

| File | Type | Lines | Purpose |
|------|------|-------|---------|
| chatbot_main.py | App | 250 | Main application ⭐ |
| chatbot.py | App | 350 | Legacy version |
| config.py | Module | 80 | Configuration |
| utils.py | Module | 150 | Utilities |
| retrieval.py | Module | 250 | RAG system |
| llm.py | Module | 200 | LLM integration |
| voice.py | Module | 280 | Voice I/O |
| README.md | Doc | 400 | Full docs |
| RUNNING.md | Doc | 300 | Quick start |
| IMPROVEMENTS.md | Doc | 600 | Technical details |
| PROFESSIONAL_SUMMARY.md | Doc | 400 | Executive summary |
| EXAMPLES.py | Code | 500 | Usage examples |
| requirements.txt | Config | 20 | Dependencies |
| .env | Config | - | Secrets |
| .gitignore | Config | - | Git rules |
| sistec_rag_data.md | Data | - | Knowledge base |

---

## 🎯 Which File Should I Use?

### **I want to...**

1. **Use the chatbot**
   - Run: `python chatbot_main.py`
   - Read: `RUNNING.md`

2. **Understand what changed**
   - Read: `PROFESSIONAL_SUMMARY.md`
   - Then: `IMPROVEMENTS.md`

3. **Get started quickly**
   - Read: `README.md`
   - Then: `RUNNING.md`

4. **Learn from the code**
   - Study: `chatbot_main.py`
   - Check: `EXAMPLES.py`
   - Reference: Module docstrings

5. **Extend or modify**
   - Edit: `config.py` (for settings)
   - Edit: `sistec_rag_data.md` (for knowledge)
   - Extended: Any module as needed

6. **Deploy to production**
   - Use: `chatbot_main.py`
   - Configure: `.env` with production secrets
   - Monitor: `chatbot.log`

7. **Integrate into my project**
   - Import: `from chatbot_main import SISTecChatbot`
   - Use: `chatbot = SISTecChatbot()`
   - Reference: `EXAMPLES.py`

---

## 🔐 Important Notes

### **Files to Never Commit to Git**
```
❌ .env                (API keys!)
❌ chatbot.log         (logs with sensitive data)
❌ __pycache__/        (Python cache)
❌ *.pyc               (Compiled Python)
```

### **Files Safe to Commit**
```
✅ All .py files (except above)
✅ All .md documentation
✅ requirements.txt
✅ .gitignore
✅ sistec_rag_data.md
```

### **Files to Keep Private**
```
🔐 .env                (Sensitive config)
🔐 API keys anywhere
🔐 User conversation logs
```

---

## 🚀 Getting Started Path

1. **Read**: `README.md` (overview)
2. **Run**: `python chatbot_main.py` (test it)
3. **Understand**: `PROFESSIONAL_SUMMARY.md` (improvements)
4. **Learn**: `EXAMPLES.py` (code examples)
5. **Deep Dive**: `IMPROVEMENTS.md` (technical details)
6. **Code**: Study individual modules (config.py, etc.)

---

## 📈 Quality Improvements

### **Code Organization**
- ✅ 8 purpose-focused files
- ✅ Clear module boundaries
- ✅ No circular dependencies

### **Documentation**
- ✅ 4 comprehensive guides
- ✅ 100% docstring coverage
- ✅ 14+ code examples
- ✅ Clear file descriptions

### **Robustness**
- ✅ Input validation
- ✅ Error handling
- ✅ Logging system
- ✅ Exception handling

### **Maintainability**
- ✅ Type hints throughout
- ✅ Consistent naming
- ✅ Clear separation of concerns
- ✅ Single responsibility principle

---

## 🎓 Learning Resources

**For Understanding the Architecture:**
- Read: `IMPROVEMENTS.md` (Before/after comparison)
- Study: `retrieval.py` (RAG implementation)
- Study: `llm.py` (LLM integration)

**For Using the Code:**
- Read: `RUNNING.md` (Quick start)
- Run: `EXAMPLES.py` (Practical examples)
- Experiment: Interactive mode

**For Best Practices:**
- Study: Module docstrings
- Review: Type hints
- Check: Error handling patterns

---

## 📚 Reference Quick Links

| Need | File | Section |
|------|------|---------|
| Installation | README.md | Installation section |
| Configuration | RUNNING.md | Configuration section |
| Quick Start | RUNNING.md | Quick Start Guide |
| Architecture | IMPROVEMENTS.md | Architecture section |
| Examples | EXAMPLES.py | All examples |
| Troubleshooting | RUNNING.md | Troubleshooting section |
| API Details | PROFESSIONAL_SUMMARY.md | Key Improvements |
| Code reference | Individual modules | Docstrings |

---

## ✨ Summary

**This complete package includes:**
- ✅ Production-ready application
- ✅ Modular, reusable components
- ✅ Comprehensive documentation
- ✅ Usage examples
- ✅ Professional code quality
- ✅ Detailed improvement guide

**Start with:** `python chatbot_main.py`

**Learn more:** See `README.md`

---

**Happy coding! 🎉**
