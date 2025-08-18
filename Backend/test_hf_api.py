#!/usr/bin/env python3
"""
Test script for Hugging Face API integration
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path so we can import from app
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'app')
sys.path.insert(0, app_dir)

load_dotenv()

def test_embeddings():
    """Test the embedding functions"""
    try:
        from matching import get_single_embedding, get_embeddings, cosine_similarity_vectors
        
        print("Testing Hugging Face API integration...")
        
        # Test single embedding
        text1 = "Hello world"
        text2 = "Hello there"
        text3 = "Python programming"
        
        print(f"Getting embedding for: '{text1}'")
        emb1 = get_single_embedding(text1)
        print(f"Embedding length: {len(emb1)}")
        print(f"First 5 values: {emb1[:5]}")
        
        # Test batch embeddings
        print(f"\nGetting batch embeddings for: {[text1, text2, text3]}")
        batch_embs = get_embeddings([text1, text2, text3])
        print(f"Batch embeddings count: {len(batch_embs)}")
        
        # Test similarity
        print(f"\nTesting similarity between '{text1}' and '{text2}'")
        similarity = cosine_similarity_vectors(emb1, batch_embs[1])
        print(f"Similarity score: {similarity:.4f}")
        
        print("\n✅ All tests passed! Hugging Face API integration is working.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Current sys.path:", sys.path)
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Check if HF_API_TOKEN is set
    if not os.getenv('HF_API_TOKEN'):
        print("❌ HF_API_TOKEN environment variable not set!")
        print("Please set it in your .env file:")
        print("HF_API_TOKEN=your_token_here")
        sys.exit(1)
    
    success = test_embeddings()
    sys.exit(0 if success else 1)
