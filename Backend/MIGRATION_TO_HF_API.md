# Migration from Local Sentence Transformers to Hugging Face API

## Overview
This migration replaces the local `sentence-transformers` model with the Hugging Face Inference API to reduce memory usage on Render deployments.

## Changes Made

### 1. Dependencies Updated
- **Removed**: `sentence-transformers>=5.0.0`
- **Added**: `requests>=2.31.0`

### 2. Code Changes in `matching.py`
- Replaced `SentenceTransformer` model loading with HTTP API calls
- Updated all embedding functions to use `get_embeddings()` and `get_single_embedding()`
- Removed `get_model()` function and global model variable
- Updated function signatures to make `model` parameter optional

### 3. New Functions Added
- `get_embeddings(texts: List[str]) -> List[List[float]]` - Batch embedding generation
- `get_single_embedding(text: str) -> List[float]` - Single text embedding
- `cosine_similarity_vectors(vec1, vec2) -> float` - Vector similarity calculation

## Environment Variables Required

Add these to your `.env` file:

```bash
# Hugging Face API Configuration
HF_API_TOKEN=your_huggingface_api_token_here
HF_MODEL_NAME=sentence-transformers/all-mpnet-base-v2
```

## How to Get Hugging Face API Token

1. Go to [Hugging Face](https://huggingface.co/)
2. Create an account or sign in
3. Go to Settings → Access Tokens
4. Create a new token with "read" permissions
5. Copy the token to your environment variables

## Benefits

- **Reduced Memory Usage**: No more loading large models into memory
- **Better Scalability**: API-based approach scales better
- **Faster Startup**: No model loading time
- **Consistent Performance**: Uses Hugging Face's optimized infrastructure

## API Costs

- **Free Tier**: 30,000 requests/month
- **Paid Plans**: Starting at $9/month for 1M requests
- **Enterprise**: Custom pricing for high-volume usage

## Fallback Behavior

If the API call fails, the system will:
1. Log the error
2. Return random embeddings (prevents crashes)
3. Continue processing with degraded accuracy

## Testing

After deployment, test the matching functionality to ensure:
1. Embeddings are generated correctly
2. Similarity calculations work as expected
3. Memory usage is significantly reduced

## Rollback Plan

If issues arise, you can rollback by:
1. Reverting the code changes
2. Re-adding `sentence-transformers` dependency
3. Restoring the original `get_model()` function
