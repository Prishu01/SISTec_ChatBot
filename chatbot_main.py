"""
Main SISTec RAG Chatbot application.

Orchestrates RAG retrieval, LLM generation, and voice I/O.
"""

# Load environment variables FIRST, before any other imports
from dotenv import load_dotenv
load_dotenv()

import logging
from pathlib import Path
from typing import Optional, Tuple

from sentence_transformers import SentenceTransformer, CrossEncoder

from config import (
    DATA_FILE, EMBED_MODEL, RERANK_MODEL, ENABLE_VOICE_OUTPUT
)
from utils import (
    setup_logger, validate_file_exists, ValidationError, ConfigError
)
from retrieval import chunk_text, build_indexes, RAGRetriever
from llm import get_llm_service, LLMService
from voice import get_voice_processor, VoiceProcessor


logger = setup_logger(__name__)


class SISTecChatbot:
    """
    Main SISTec RAG Chatbot class.
    
    Integrates retrieval, LLM generation, and voice processing
    for a complete conversational AI experience.
    """
    
    def __init__(self, knowledge_base_path: str = DATA_FILE,
                 enable_voice: bool = ENABLE_VOICE_OUTPUT):
        """
        Initialize SISTec Chatbot.
        
        Args:
            knowledge_base_path: Path to knowledge base markdown file
            enable_voice: Whether to enable voice input/output
            
        Raises:
            ConfigError: If initialization fails
        """
        logger.info("Initializing SISTec Chatbot...")
        
        try:
            # Validate knowledge base file
            if not validate_file_exists(knowledge_base_path):
                raise ConfigError(f"Knowledge base not found: {knowledge_base_path}")
            
            # Load and process knowledge base
            logger.info("Loading knowledge base...")
            with open(knowledge_base_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            logger.info(f"Knowledge base loaded: {len(text)} characters")
            
            # Chunk text
            logger.info("Chunking knowledge base...")
            chunks = chunk_text(text)
            
            # Load embedding model
            logger.info(f"Loading embedding model: {EMBED_MODEL}")
            embed_model = SentenceTransformer(EMBED_MODEL)
            
            # Load reranking model
            logger.info(f"Loading reranking model: {RERANK_MODEL}")
            reranker = CrossEncoder(RERANK_MODEL)
            
            # Build indexes
            logger.info("Building retrieval indexes...")
            faiss_index, bm25_index = build_indexes(chunks, embed_model)
            
            # Initialize RAG retriever
            self.retriever = RAGRetriever(chunks, embed_model, reranker)
            self.retriever.set_indexes(faiss_index, bm25_index)
            
            # Initialize LLM service
            self.llm_service = get_llm_service()
            
            # Initialize voice processor
            self.voice_processor = get_voice_processor(enable_voice=enable_voice)
            
            # State tracking
            self.conversation_history = []
            self.enable_voice = enable_voice
            
            logger.info("✅ Chatbot initialized successfully!")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise ConfigError(f"Failed to initialize chatbot: {e}")
    
    def answer_question(self, question: str, show_context: bool = False) -> str:
        """
        Answer a user question using RAG + LLM.
        
        Args:
            question: User question
            show_context: Whether to include context in response
            
        Returns:
            Generated answer
        """
        if not question or not isinstance(question, str):
            logger.warning("Invalid question provided")
            return "Please provide a valid question."
        
        logger.info(f"Processing question: {question[:50]}...")
        
        try:
            # Retrieve context using RAG
            context, ranked_chunks = self.retriever.retrieve(question)
            
            # Generate response using LLM
            answer = self.llm_service.generate_response(question, context)
            
            # Track in conversation history
            self.conversation_history.append({
                "question": question,
                "answer": answer,
                "context_chunks": len(ranked_chunks)
            })
            
            # Optionally show context
            if show_context and ranked_chunks:
                logger.info(f"Retrieved {len(ranked_chunks)} relevant chunks")
            
            return answer
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return "I encountered an error processing your question. Please try again."
    
    def voice_input(self, duration: int = 5) -> str:
        """
        Get user input via voice.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Recognized text, or empty string if failed
        """
        return self.voice_processor.record_voice(duration)
    
    def voice_output(self, text: str) -> bool:
        """
        Output response via voice.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            True if successful, False otherwise
        """
        return self.voice_processor.text_to_speech(text)
    
    def interactive_session(self) -> None:
        """
        Start interactive chat session.
        
        Provides CLI interface for chatting with the bot.
        """
        self._print_banner()
        self._print_commands()
        
        while True:
            try:
                user_input = input("\n📝 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() == "help":
                    self._print_commands()
                    continue
                
                if user_input.lower() == "history":
                    self._print_history()
                    continue
                
                if user_input.lower() == "exit":
                    self._print_goodbye()
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
                
                # Generate and display response
                print("\n⏳ Thinking...")
                answer = self.answer_question(question)
                
                print(f"\n🤖 Bot: {answer}")
                
                # Output via voice if enabled
                if self.enable_voice:
                    self.voice_output(answer)
                
            except KeyboardInterrupt:
                print("\n\n⏹️ Chat interrupted")
                break
                
            except Exception as e:
                logger.error(f"Session error: {e}")
                print(f"❌ Error: {e}")
    
    def _print_banner(self) -> None:
        """Print welcome banner."""
        print("\n" + "="*60)
        print("🎓 SAGAR GROUP OF INSTITUTIONS (SGI) - AI Chatbot")
        print("Powered by RAG + LLM + Voice Technology")
        print("="*60)
    
    def _print_commands(self) -> None:
        """Print available commands."""
        commands = """
📚 Commands:
  <question>      - Ask a text question
  voice [N]       - Record voice input (N seconds, default=5)
  history         - Show conversation history
  help            - Show this help message
  exit            - Exit chatbot
        """
        print(commands)
    
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
            print(f"    Chunks used: {item['context_chunks']}")
        
        print("-" * 60)
    
    def _print_goodbye(self) -> None:
        """Print goodbye message."""
        print("\n" + "="*60)
        print("👋 Thank you for using SGI Chatbot!")
        print("="*60)
    
    def get_conversation_history(self) -> list:
        """Get full conversation history."""
        return self.conversation_history
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")


def main() -> None:
    """Main entry point for the chatbot."""
    try:
        # Initialize chatbot
        chatbot = SISTecChatbot(enable_voice=ENABLE_VOICE_OUTPUT)
        
        # Start interactive session
        chatbot.interactive_session()
        
    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Configuration Error: {e}")
        print("\n📋 Setup Instructions:")
        print("1. Ensure sistec_rag_data.md exists in the project folder")
        print("2. Set GROQ_API_KEY in .env file")
        print("3. Try running the chatbot again")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal Error: {e}")


if __name__ == "__main__":
    main()
