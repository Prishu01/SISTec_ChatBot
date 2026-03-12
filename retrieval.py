"""
Retrieval Augmented Generation (RAG) module.

Handles document chunking, indexing, and hybrid retrieval with reranking.
"""

import logging
from typing import List, Tuple
import numpy as np

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
import faiss

from config import (
    CHUNK_SIZE, CHUNK_OVERLAP, BM25_TOP_K, FAISS_TOP_K,
    RERANK_TOP_K, ALPHA, EMBED_MODEL, RERANK_MODEL
)
from utils import setup_logger, ValidationError

logger = setup_logger(__name__)


class RAGRetriever:
    """
    Hybrid Retrieval Augmented Generation system.
    
    Combines BM25, FAISS vector search, and CrossEncoder reranking
    for comprehensive context retrieval.
    """
    
    def __init__(self, chunks: List[str], embed_model: SentenceTransformer,
                 reranker: CrossEncoder):
        """
        Initialize RAG retriever with pre-built indexes.
        
        Args:
            chunks: List of document chunks
            embed_model: SentenceTransformer for embeddings
            reranker: CrossEncoder for reranking
            
        Raises:
            ValidationError: If chunks list is empty
        """
        if not chunks:
            raise ValidationError("Chunks list cannot be empty")
        
        self.chunks = chunks
        self.embed_model = embed_model
        self.reranker = reranker
        self.faiss_index: faiss.IndexFlatL2 = None
        self.bm25_index: BM25Okapi = None
        
        logger.info(f"Initialized RAGRetriever with {len(chunks)} chunks")
    
    def set_indexes(self, faiss_index: faiss.IndexFlatL2,
                    bm25_index: BM25Okapi) -> None:
        """
        Set pre-built FAISS and BM25 indexes.
        
        Args:
            faiss_index: Pre-built FAISS index
            bm25_index: Pre-built BM25 index
        """
        self.faiss_index = faiss_index
        self.bm25_index = bm25_index
        logger.info("Indexes set for RAGRetriever")
    
    def hybrid_retrieve(self, query: str) -> List[str]:
        """
        Retrieve candidates using hybrid approach (BM25 + FAISS).
        
        Implements Reciprocal Rank Fusion (RRF) to combine scores from
        two different retrieval methods.
        
        Args:
            query: User query text
            
        Returns:
            List of relevant chunks
            
        Raises:
            ValidationError: If query is empty or indexes not set
        """
        if not query or not query.strip():
            raise ValidationError("Query cannot be empty")
        
        if not self.bm25_index or not self.faiss_index:
            raise ValidationError("Indexes not initialized")
        
        # BM25 retrieval
        bm25_scores = self.bm25_index.get_scores(query.lower().split())
        bm25_top_idx = np.argsort(bm25_scores)[::-1][:BM25_TOP_K]
        
        logger.debug(f"BM25 retrieved {len(bm25_top_idx)} candidates")
        
        # FAISS vector search
        query_embedding = self.embed_model.encode([query], convert_to_numpy=True)
        _, faiss_top_idx = self.faiss_index.search(
            np.array(query_embedding, dtype=np.float32),
            FAISS_TOP_K
        )
        
        faiss_top_idx = faiss_top_idx[0]
        logger.debug(f"FAISS retrieved {len(faiss_top_idx)} candidates")
        
        # Reciprocal Rank Fusion (RRF)
        rrf_scores = {}
        
        # BM25 scores
        for rank, idx in enumerate(bm25_top_idx):
            rrf_scores[int(idx)] = rrf_scores.get(int(idx), 0) + (1 - ALPHA) / (rank + 1)
        
        # FAISS scores
        for rank, idx in enumerate(faiss_top_idx):
            idx = int(idx)
            rrf_scores[idx] = rrf_scores.get(idx, 0) + ALPHA / (rank + 1)
        
        # Sort by RRF score
        sorted_idx = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        candidates = [self.chunks[idx] for idx, _ in sorted_idx]
        
        logger.info(f"Hybrid retrieval returned {len(candidates)} candidates")
        return candidates
    
    def retrieve(self, query: str) -> Tuple[str, List[Tuple[float, str]]]:
        """
        Retrieve and rerank context for a query.
        
        Args:
            query: User query text
            
        Returns:
            Tuple of (combined context string, list of ranked chunks with scores)
            
        Raises:
            ValidationError: If query is invalid
        """
        candidates = self.hybrid_retrieve(query)
        
        if not candidates:
            logger.warning(f"No candidates found for query: {query}")
            return "No relevant information found in knowledge base.", []
        
        # Rerank using CrossEncoder
        scores = self.reranker.predict([[query, chunk] for chunk in candidates])
        
        # Combine scores and candidates
        ranked: List[Tuple[float, str]] = sorted(
            zip(scores, candidates),
            reverse=True
        )
        
        # Get top-K
        top_ranked = ranked[:RERANK_TOP_K]
        
        # Combine into context string
        context = "\n\n".join([chunk for _, chunk in top_ranked])
        
        logger.info(f"Retrieved {len(top_ranked)} reranked contexts")
        return context, top_ranked


def build_indexes(chunks: List[str],
                  embed_model: SentenceTransformer) -> Tuple[faiss.IndexFlatL2, BM25Okapi]:
    """
    Build FAISS and BM25 indexes from chunks.
    
    Args:
        chunks: List of text chunks
        embed_model: SentenceTransformer model for embeddings
        
    Returns:
        Tuple of (FAISS index, BM25 index)
        
    Raises:
        ValidationError: If chunks are invalid
    """
    if not chunks:
        raise ValidationError("Cannot build indexes with empty chunks")
    
    logger.info(f"Building indexes for {len(chunks)} chunks...")
    
    # Build FAISS index
    logger.info("Building FAISS vector index...")
    embeddings = embed_model.encode(chunks, batch_size=32, show_progress_bar=False)
    
    faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
    faiss_index.add(np.array(embeddings, dtype=np.float32))
    logger.info(f"FAISS index built with {len(embeddings)} vectors")
    
    # Build BM25 index
    logger.info("Building BM25 index...")
    bm25_index = BM25Okapi([chunk.lower().split() for chunk in chunks])
    logger.info(f"BM25 index built")
    
    return faiss_index, bm25_index


def chunk_text(text: str) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Input text to chunk
        
    Returns:
        List of text chunks
        
    Raises:
        ValidationError: If text is empty
    """
    if not text or not text.strip():
        raise ValidationError("Cannot chunk empty text")
    
    logger.info(f"Chunking {len(text)} characters with size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = splitter.split_text(text)
    logger.info(f"Created {len(chunks)} chunks")
    
    return chunks
