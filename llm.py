"""
Large Language Model (LLM) integration module.

Handles communication with Groq API and prompt management.
"""

import logging
from typing import Optional
from groq import Groq
from groq import APIError as GroqAPIError

from config import GROQ_MODEL, GROQ_API_KEY
from utils import setup_logger, validate_api_key, sanitize_text, ValidationError

logger = setup_logger(__name__)


SYSTEM_PROMPT = """You are a professional, helpful AI assistant for SISTec (Sagar Group of Institutions), Bhopal.

Your responsibilities:
1. Answer questions ONLY using the provided context
2. Be accurate, concise, and professional
3. If information is not in the context, clearly state: "I don't have that information in my knowledge base."
4. Keep responses brief (2-4 sentences) unless more detail is requested
5. Cite relevant information from the context when applicable
6. Maintain a friendly and professional tone

Always prioritize accuracy over providing an answer."""


class LLMService:
    """
    Service for interacting with Groq LLM API.
    
    Manages API requests, error handling, and prompt templates.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = GROQ_MODEL):
        """
        Initialize LLM service.
        
        Args:
            api_key: Groq API key (uses config if not provided)
            model: Model name to use
            
        Raises:
            ValidationError: If API key is missing or invalid
        """
        api_key = api_key or GROQ_API_KEY
        
        if not validate_api_key(api_key):
            raise ValidationError(
                "Invalid or missing GROQ_API_KEY. "
                "Set it in .env file or environment variables."
            )
        
        self.client = Groq(api_key=api_key)
        self.model = model
        
        logger.info(f"LLMService initialized with model: {model}")
    
    def generate_response(self, question: str, context: str,
                         system_prompt: Optional[str] = None) -> str:
        """
        Generate LLM response to a question using provided context.
        
        Args:
            question: User question
            context: Retrieved context from knowledge base
            system_prompt: Custom system prompt (uses default if not provided)
            
        Returns:
            Generated response text
            
        Raises:
            ValidationError: If question or context is invalid
            GroqAPIError: If API call fails
        """
        if not question or not isinstance(question, str):
            raise ValidationError("Question must be a non-empty string")
        
        if not context or not isinstance(context, str):
            raise ValidationError("Context must be a non-empty string")
        
        question = sanitize_text(question)
        context = sanitize_text(context, max_length=8000)
        system_prompt = system_prompt or SYSTEM_PROMPT
        
        # Construct the user prompt
        user_message = self._build_prompt(question, context)
        
        logger.info(f"Generating response for: {question[:50]}...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                temperature=0.3,  # Lower temperature for consistency
                max_tokens=500,
                top_p=0.9
            )
            
            answer = response.choices[0].message.content
            logger.info("Response generated successfully")
            
            return answer
            
        except GroqAPIError as e:
            logger.error(f"Groq API error: {e}")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error during LLM generation: {e}")
            raise
    
    def _build_prompt(self, question: str, context: str) -> str:
        """
        Build user prompt with context and question.
        
        Args:
            question: User question
            context: Retrieved context
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Based on the following context from SISTec knowledge base:

---CONTEXT START---
{context}
---CONTEXT END---

Question: {question}

Answer:"""
        return prompt
    
    def validate_connection(self) -> bool:
        """
        Validate connection to Groq API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info("Validating Groq API connection...")
            
            # Make a minimal test request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "test"}
                ],
                max_tokens=10
            )
            
            logger.info("Groq API connection validated")
            return True
            
        except Exception as e:
            logger.error(f"Groq API connection failed: {e}")
            return False


def get_llm_service(api_key: Optional[str] = None) -> LLMService:
    """
    Factory function to create or get LLMService instance.
    
    Args:
        api_key: Optional API key override
        
    Returns:
        LLMService instance
        
    Raises:
        ValidationError: If configuration is invalid
    """
    try:
        return LLMService(api_key=api_key)
    except ValidationError as e:
        logger.error(f"Failed to initialize LLMService: {e}")
        raise
