#!/usr/bin/env python3
"""
Embeddings Generator for Compliance Documents
Generates OpenAI embeddings with dimension reduction support
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from openai import OpenAI
import tiktoken
import logging
import time
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(env_path)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EmbeddingsGenerator:
    """Generate embeddings using OpenAI API with dimension reduction"""

    def __init__(self, model: str = None, dimension: int = None):
        """
        Initialize embeddings generator.

        Args:
            model: Embedding model name (default from env)
            dimension: Embedding dimension (default from env)
        """
        # Get configuration
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
        self.dimension = dimension or int(os.getenv("EMBEDDING_DIMENSION", "1024"))

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)

        # Initialize tokenizer for counting
        try:
            self.tokenizer = tiktoken.encoding_for_model(self.model)
        except:
            # Fallback to cl100k_base encoding for newer models
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

        logger.info(f"Initialized embeddings generator:")
        logger.info(f"  Model: {self.model}")
        logger.info(f"  Dimension: {self.dimension}")

        # Track usage for cost estimation
        self.total_tokens = 0
        self.total_requests = 0

    def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of texts with batching.

        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process in one API call

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        all_embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size

        logger.info(f"Generating embeddings for {len(texts)} texts in {total_batches} batches")

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = (i // batch_size) + 1

            try:
                # Generate embeddings with dimension reduction
                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} texts)")

                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model,
                    dimensions=self.dimension  # Dimension reduction happens here!
                )

                # Extract embeddings
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

                # Track usage
                self.total_requests += 1
                batch_tokens = sum(len(self.tokenizer.encode(text)) for text in batch)
                self.total_tokens += batch_tokens

                logger.info(f"  Generated {len(batch_embeddings)} embeddings ({batch_tokens:,} tokens)")

                # Rate limiting (be nice to the API)
                if batch_num < total_batches:
                    time.sleep(0.1)  # Small delay between batches

            except Exception as e:
                logger.error(f"Error generating embeddings for batch {batch_num}: {str(e)}")
                # Return empty embeddings for failed batch
                all_embeddings.extend([[0.0] * self.dimension] * len(batch))

        logger.info(f"Successfully generated {len(all_embeddings)} embeddings")
        return all_embeddings

    def generate_single_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to embed

        Returns:
            Embedding vector
        """
        embeddings = self.generate_embeddings([text])
        return embeddings[0] if embeddings else [0.0] * self.dimension

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in a text string.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        return len(self.tokenizer.encode(text))

    def estimate_cost(self, texts: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Estimate embedding cost.

        Args:
            texts: Optional list of texts to estimate cost for

        Returns:
            Dictionary with cost estimates
        """
        # Pricing per 1M tokens (as of 2024)
        pricing = {
            "text-embedding-3-small": 0.02,  # $0.02 per 1M tokens
            "text-embedding-3-large": 0.13,  # $0.13 per 1M tokens
            "text-embedding-ada-002": 0.10,  # $0.10 per 1M tokens
        }

        model_price = pricing.get(self.model, 0.13)  # Default to large price

        if texts:
            # Estimate for provided texts
            total_tokens = sum(self.count_tokens(text) for text in texts)
            estimated_cost = (total_tokens / 1_000_000) * model_price

            return {
                "texts": len(texts),
                "estimated_tokens": total_tokens,
                "estimated_cost": round(estimated_cost, 4),
                "model": self.model,
                "price_per_1m_tokens": model_price
            }
        else:
            # Return actual usage
            actual_cost = (self.total_tokens / 1_000_000) * model_price

            return {
                "total_requests": self.total_requests,
                "total_tokens": self.total_tokens,
                "actual_cost": round(actual_cost, 4),
                "model": self.model,
                "price_per_1m_tokens": model_price
            }

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1500,
        overlap: int = 200
    ) -> List[Dict[str, any]]:
        """
        Chunk text for embedding with overlap.

        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Number of overlapping characters

        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunks = []
        start = 0
        text_length = len(text)
        chunk_num = 0

        while start < text_length:
            # Calculate end position
            end = min(start + chunk_size, text_length)

            # Try to break at sentence boundary
            if end < text_length:
                # Look for sentence end
                last_period = text.rfind('. ', start, end)
                if last_period > start + (chunk_size // 2):
                    end = last_period + 1

            # Extract chunk
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'chunk_index': chunk_num,
                    'start_char': start,
                    'end_char': end,
                    'char_count': len(chunk_text),
                    'token_count': self.count_tokens(chunk_text)
                })
                chunk_num += 1

            # Move start position
            start = end - overlap if end < text_length else text_length

        logger.info(f"Created {len(chunks)} chunks from {text_length:,} characters")
        return chunks


def main():
    """Test the embeddings generator"""

    generator = EmbeddingsGenerator()

    # Test texts
    test_texts = [
        "The Federal Risk and Authorization Management Program (FedRAMP) provides a standardized approach to security assessment.",
        "CMMC 2.0 is the Cybersecurity Maturity Model Certification framework for defense contractors.",
        "NIST 800-171 provides guidelines for protecting Controlled Unclassified Information (CUI)."
    ]

    print(f"Testing embeddings generation...")
    print(f"Model: {generator.model}")
    print(f"Dimension: {generator.dimension}")

    # Generate embeddings
    embeddings = generator.generate_embeddings(test_texts)

    print(f"\n=== Results ===")
    print(f"Generated {len(embeddings)} embeddings")

    for i, (text, embedding) in enumerate(zip(test_texts, embeddings)):
        print(f"\nText {i + 1}: {text[:50]}...")
        print(f"  Embedding dimension: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
        print(f"  Token count: {generator.count_tokens(text)}")

    # Estimate cost
    cost_info = generator.estimate_cost()
    print(f"\n=== Cost Information ===")
    print(f"Model: {cost_info['model']}")
    print(f"Price per 1M tokens: ${cost_info['price_per_1m_tokens']}")
    print(f"Total tokens used: {cost_info['total_tokens']:,}")
    print(f"Actual cost: ${cost_info['actual_cost']}")

    # Test chunking
    long_text = " ".join(test_texts * 10)
    chunks = generator.chunk_text(long_text, chunk_size=500, overlap=50)
    print(f"\n=== Chunking Test ===")
    print(f"Original text: {len(long_text):,} characters")
    print(f"Created {len(chunks)} chunks")
    print(f"Average chunk size: {sum(c['char_count'] for c in chunks) / len(chunks):.0f} characters")
    print(f"Average tokens per chunk: {sum(c['token_count'] for c in chunks) / len(chunks):.0f}")


if __name__ == "__main__":
    main()