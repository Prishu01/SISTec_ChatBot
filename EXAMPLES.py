"""
Example tests and usage patterns for SISTec Chatbot.

Demonstrates how to use the refactored chatbot modules
in various scenarios (testing, integration, scripts).
"""

# Example 1: Basic Usage
# ============================================================================

from chatbot_main import SISTecChatbot

# Initialize the chatbot
chatbot = SISTecChatbot(enable_voice=False)

# Ask a question
answer = chatbot.answer_question("What are the departments at SGI?")
print(f"Answer: {answer}")

# Check conversation history
history = chatbot.get_conversation_history()
print(f"Questions asked: {len(history)}")


# Example 2: Multiple Questions
# ============================================================================

questions = [
    "What is SGI?",
    "Tell me about the engineering department",
    "What are the admission requirements?",
    "Do you have campus facilities?"
]

for question in questions:
    answer = chatbot.answer_question(question)
    print(f"Q: {question}\nA: {answer}\n")

# Print summary
print(f"Total Q&A pairs: {len(chatbot.conversation_history)}")


# Example 3: Voice Input/Output
# ============================================================================

# With voice enabled
chatbot_voice = SISTecChatbot(enable_voice=True)

# Get voice input (5 seconds)
voice_question = chatbot_voice.voice_input(duration=5)

if voice_question:
    # Answer the question
    answer = chatbot.answer_question(voice_question)
    
    # Speak the answer
    chatbot_voice.voice_output(answer)


# Example 4: RAG Retriever Usage
# ============================================================================

from retrieval import RAGRetriever
from sentence_transformers import SentenceTransformer, CrossEncoder

# Access the retriever
retriever = chatbot.retriever

# Retrieve context for a query
query = "campus facilities"
context, ranked_chunks = retriever.retrieve(query)

print(f"Context for '{query}':")
print(context)
print(f"\nRetrieved {len(ranked_chunks)} chunks")


# Example 5: LLM Service Usage
# ============================================================================

from llm import LLMService

# Get the LLM service
llm = chatbot.llm_service

# Generate custom response
context = "SGI has 3 departments: Engineering, Pharmacy, Management"
question = "How many departments does SGI have?"

response = llm.generate_response(question, context)
print(f"Response: {response}")

# Validate API connection
if llm.validate_connection():
    print("✅ Groq API is connected")
else:
    print("❌ Groq API connection failed")


# Example 6: Voice Processor Usage
# ============================================================================

from voice import get_voice_processor

# Get voice processor
voice = get_voice_processor(enable_voice=True)

# Record voice input
text = voice.record_voice(duration=10)
print(f"You said: {text}")

# Convert text to speech
voice.text_to_speech("Hello! This is the SGI chatbot.")


# Example 7: Configuration Usage
# ============================================================================

import config

# Access configuration
print(f"Embedding model: {config.EMBED_MODEL}")
print(f"Reranking model: {config.RERANK_MODEL}")
print(f"Chunk size: {config.CHUNK_SIZE}")
print(f"Voice enabled: {config.ENABLE_VOICE_OUTPUT}")

# Override configuration (for testing)
config.CHUNK_SIZE = 1024
config.ALPHA = 0.6


# Example 8: Utilities Usage
# ============================================================================

from utils import (
    validate_api_key, validate_duration, 
    sanitize_text, setup_logger
)

# Setup logger
logger = setup_logger(__name__)
logger.info("This is an info message")
logger.warning("This is a warning")
logger.error("This is an error")

# Validate inputs
api_key = "gsk_1234567890abcdef"
if validate_api_key(api_key):
    print("✅ API key is valid")

# Validate duration
if validate_duration(5):
    print("✅ Duration is valid")

# Sanitize text
dirty_text = "This   has    extra     spaces"
clean = sanitize_text(dirty_text)
print(f"Cleaned: '{clean}'")


# Example 9: Error Handling
# ============================================================================

from utils import ValidationError, ConfigError

try:
    # This will raise ValidationError
    chatbot.answer_question("")
    
except ValidationError as e:
    print(f"Validation Error: {e}")
    
except ConfigError as e:
    print(f"Config Error: {e}")
    
except Exception as e:
    print(f"Unexpected Error: {e}")


# Example 10: Full Integration Example
# ============================================================================

def run_interactive_demo():
    """
    Full demo of all chatbot features.
    """
    
    # Initialize with all features
    chatbot = SISTecChatbot(enable_voice=False)  # Text mode
    
    print("\n" + "="*60)
    print("SISTec Chatbot - Complete Demonstration")
    print("="*60)
    
    # Demo 1: Text Q&A
    print("\n[1] Text Q&A Demo")
    print("-" * 40)
    
    demo_questions = [
        "What is SGI?",
        "Tell me about campus facilities"
    ]
    
    for q in demo_questions:
        answer = chatbot.answer_question(q)
        print(f"Q: {q}")
        print(f"A: {answer}\n")
    
    # Demo 2: History
    print("[2] Conversation History")
    print("-" * 40)
    history = chatbot.get_conversation_history()
    print(f"Total interactions: {len(history)}")
    
    for i, item in enumerate(history, 1):
        print(f"  {i}. {item['question'][:40]}...")
    
    # Demo 3: Retriever
    print("\n[3] RAG Retrieval Demo")
    print("-" * 40)
    
    query = "departments"
    context, chunks = chatbot.retriever.retrieve(query)
    print(f"Query: '{query}'")
    print(f"Retrieved chunks: {len(chunks)}")
    print(f"First chunk score: {chunks[0][0]:.4f}")
    
    print("\n" + "="*60)
    print("✅ Demo Complete!")
    print("="*60)


# Example 11: Unit Testing Mock
# ============================================================================

def test_knowledge_base_loading():
    """Test that knowledge base loads correctly."""
    from pathlib import Path
    
    kb_path = Path("sistec_rag_data.md")
    assert kb_path.exists(), "Knowledge base file not found"
    assert kb_path.stat().st_size > 0, "Knowledge base is empty"
    print("✅ Knowledge base loading test passed")


def test_api_configuration():
    """Test API configuration."""
    from config import GROQ_API_KEY
    
    assert GROQ_API_KEY is not None, "API key not configured"
    assert len(GROQ_API_KEY) > 20, "API key appears invalid"
    print("✅ API configuration test passed")


def test_text_sanitization():
    """Test text sanitization utility."""
    from utils import sanitize_text
    
    test_cases = [
        ("hello   world", "hello world"),
        ("  spaces  ", "spaces"),
        ("hello" * 1000 + "x", "hello" * 1000 + "x" + "...")
    ]
    
    for input_text, expected_prefix in test_cases:
        result = sanitize_text(input_text)
        assert result.startswith(expected_prefix.replace("...", "")), \
            f"Sanitization failed for: {input_text}"
    
    print("✅ Text sanitization tests passed")


# Example 12: Performance Benchmarking
# ============================================================================

import time

def benchmark_retrieval():
    """Benchmark the retrieval system."""
    chatbot = SISTecChatbot(enable_voice=False)
    
    queries = [
        "departments",
        "campus facilities",
        "admission",
        "faculty",
        "courses"
    ]
    
    print("\nRetrieval Performance Benchmark:")
    print("-" * 50)
    
    total_time = 0
    
    for query in queries:
        start = time.time()
        context, chunks = chatbot.retriever.retrieve(query)
        elapsed = time.time() - start
        
        total_time += elapsed
        print(f"  {query:20} - {elapsed*1000:6.2f} ms")
    
    avg_time = total_time / len(queries)
    print("-" * 50)
    print(f"  Average retrieval time: {avg_time*1000:.2f} ms")


# Example 13: Custom Prompt Engineering
# ============================================================================

from llm import LLMService

def custom_response_generation():
    """Generate response with custom system prompt."""
    
    llm = SISTecChatbot(enable_voice=False).llm_service
    
    custom_system_prompt = """You are a helpful SGI tour guide.
    Always be enthusiastic and provide details about campus life.
    Keep responses friendly and welcoming."""
    
    question = "Tell me about the campus"
    context = "SGI has a 50-acre campus with modern facilities..."
    
    # Note: generate_response doesn't support custom system prompt in current version
    # This shows how it could be extended
    response = llm.generate_response(question, context)
    print(f"Custom Response: {response}")


# Example 14: Batch Processing
# ============================================================================

def batch_process_questions(questions_file: str):
    """
    Process multiple questions from a file.
    
    File format: one question per line
    """
    chatbot = SISTecChatbot(enable_voice=False)
    
    try:
        with open(questions_file, 'r') as f:
            questions = [line.strip() for line in f if line.strip()]
        
        results = []
        
        for i, question in enumerate(questions, 1):
            print(f"Processing {i}/{len(questions)}: {question[:40]}...")
            
            answer = chatbot.answer_question(question)
            results.append({
                'question': question,
                'answer': answer
            })
        
        return results
        
    except FileNotFoundError:
        print(f"File not found: {questions_file}")
        return []


# Main execution
# ============================================================================

if __name__ == "__main__":
    print("SISTec Chatbot - Usage Examples")
    print("="*60)
    
    # Run tests
    print("\n[Running Tests...]")
    try:
        test_knowledge_base_loading()
        test_api_configuration()
        test_text_sanitization()
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    
    # Run benchmark
    print("\n[Running Benchmark...]")
    benchmark_retrieval()
    
    # Run demo
    print("\n[Running Demo...]")
    run_interactive_demo()
    
    print("\n✅ All examples completed!")
