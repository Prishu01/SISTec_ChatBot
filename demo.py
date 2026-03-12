import logging
from pathlib import Path
from typing import Optional

from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

from config import (
    DATA_FILE, EMBED_MODEL, ENABLE_VOICE_OUTPUT
)
from utils import (
    setup_logger, validate_file_exists, ValidationError, ConfigError
)
from retrieval import chunk_text, build_indexes
from llm import get_llm_service, LLMService
from voice import get_voice_processor, VoiceProcessor


logger = setup_logger(__name__)


class SimpleChatbot:
    """
    Simplified SISTec Chatbot without reranking.
    
    Fast initialization useful for demos and testing.
    Skips the CrossEncoder reranker.
    """
    
    def __init__(self, knowledge_base_path: str = DATA_FILE,
                 enable_voice: bool = ENABLE_VOICE_OUTPUT):
        """Initialize simplified chatbot without reranker."""
        
        logger.info("Initializing SISTec Chatbot (Demo Mode - No Reranker)...")
        
        try:
            # Validate knowledge base file
            if not validate_file_exists(knowledge_base_path):
                raise ConfigError(f"Knowledge base not found: {knowledge_base_path}")
            
            # Load knowledge base
            logger.info("Loading knowledge base...")
            with open(knowledge_base_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            logger.info(f"Knowledge base loaded: {len(text)} characters")
            
            # Chunk text
            logger.info("Chunking knowledge base...")
            chunks = chunk_text(text)
            
            # Load embedding model only (skip reranker)
            logger.info(f"Loading embedding model: {EMBED_MODEL}")
            embed_model = SentenceTransformer(EMBED_MODEL)
            
            # Build indexes (without reranker)
            logger.info("Building retrieval indexes...")
            faiss_index, bm25_index = build_indexes(chunks, embed_model)
            
            self.chunks = chunks
            self.embed_model = embed_model
            self.faiss_index = faiss_index
            self.bm25_index = bm25_index
            
            # Initialize LLM service
            self.llm_service = get_llm_service()
            
            # Initialize voice processor
            self.voice_processor = get_voice_processor(enable_voice=enable_voice)
            
            # State tracking
            self.conversation_history = []
            self.enable_voice = enable_voice
            
            logger.info("✅ Demo Chatbot initialized successfully!")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise ConfigError(f"Failed to initialize chatbot: {e}")
    
    def simple_retrieve(self, query: str) -> str:
        """Simple retrieval without reranking."""
        import numpy as np
        from rank_bm25 import BM25Okapi
        
        # BM25 retrieval
        bm25_scores = self.bm25_index.get_scores(query.lower().split())
        bm25_top_idx = np.argsort(bm25_scores)[::-1][:5]  # Top 5
        
        # Return top chunks
        context = "\n\n".join([self.chunks[int(idx)] for idx in bm25_top_idx])
        return context
    
    def answer_question(self, question: str) -> str:
        """Answer a question using simple retrieval."""
        
        if not question or not isinstance(question, str):
            logger.warning("Invalid question provided")
            return "Please provide a valid question."
        
        logger.info(f"Processing question: {question[:50]}...")
        
        try:
            # Simple retrieval
            context = self.simple_retrieve(question)
            
            # Generate response using LLM
            answer = self.llm_service.generate_response(question, context)
            
            # Track in conversation history
            self.conversation_history.append({
                "question": question,
                "answer": answer,
                "mode": "demo"
            })
            
            return answer
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return "I encountered an error processing your question. Please try again."
    
    def voice_input(self, duration: int = 5) -> str:
        """Get user input via voice."""
        return self.voice_processor.record_voice(duration)
    
    def voice_output(self, text: str) -> bool:
        """Output response via voice."""
        return self.voice_processor.text_to_speech(text)
    
    def interactive_session(self) -> None:
        """Start interactive chat session."""
        
        print("\n" + "="*60)
        print("🎓 SAGAR GROUP OF INSTITUTIONS (SGI) - AI Chatbot")
        print("Demo Mode (No Reranker - Fast Initialization)")
        print("="*60)
        
        commands = """
📚 Commands:
  <question>      - Ask a text question
  voice [N]       - Record voice input (N seconds, default=5)
  history         - Show conversation history
  help            - Show this help message
  exit            - Exit chatbot
        """
        print(commands)
        
        while True:
            try:
                user_input = input("\n📝 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == "help":
                    print(commands)
                    continue
                
                if user_input.lower() == "history":
                    self._print_history()
                    continue
                
                if user_input.lower() == "exit":
                    print("\n" + "="*60)
                    print("👋 Thank you for using SGI Chatbot!")
                    print("="*60)
                    if self.enable_voice:
                        self.voice_output("Goodbye!")
                    break
                
                if user_input.lower().startswith("voice"):
                    parts = user_input.split()
                    duration = 5
                    
                    if len(parts) > 1 and parts[1].isdigit():
                        duration = int(parts[1])
                    
                    question = self.voice_input(duration)
                    
                    if not question:
                        print("❌ Could not capture voice input")
                        continue
                else:
                    question = user_input
                
                # Generate response
                print("\n⏳ Thinking...")
                answer = self.answer_question(question)
                
                print(f"\n🤖 Bot: {answer}")
                
                # Voice output if enabled
                if self.enable_voice:
                    self.voice_output(answer)
                
            except KeyboardInterrupt:
                print("\n\n⏹️ Chat interrupted")
                break
                
            except Exception as e:
                logger.error(f"Session error: {e}")
                print(f"❌ Error: {e}")
    
    def _print_history(self) -> None:
        """Print conversation history."""
        if not self.conversation_history:
            print("\n📭 No conversation history yet")
            return
        
        print("\n📋 Conversation History:")
        print("-" * 60)
        
        for i, item in enumerate(self.conversation_history, 1):
            print(f"\n[{i}] Q: {item['question'][:60]}...")
            print(f"    A: {item['answer'][:80]}...")
        
        print("-" * 60)
    
    def get_conversation_history(self) -> list:
        """Get full conversation history."""
        return self.conversation_history


def main() -> None:
    """Main entry point for demo chatbot."""
    try:
        # Initialize chatbot
        chatbot = SimpleChatbot(enable_voice=ENABLE_VOICE_OUTPUT)
        
        # Start interactive session
        chatbot.interactive_session()
        
    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Configuration Error: {e}")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal Error: {e}")


if __name__ == "__main__":
    main()
