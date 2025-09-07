# RAG Evaluation Datasets

This directory contains datasets for RAG evaluation with content-addressed storage and deterministic splits.

## Dataset Management

### Content-Addressed Storage
- Datasets are identified by SHA-256 hashes for reproducibility
- Large corpora are stored out-of-repo to avoid bloating the repository
- Dataset metadata includes version, creation date, and hash

### Split Policy
- **Train/Validation/Test**: 70/15/15 split with deterministic seeds
- **Reproducibility**: All splits use fixed random seeds for consistent results
- **Versioning**: Dataset versions are tracked with semantic versioning

## Dataset Format

```json
{
  "version": "1.0.0",
  "created_at": "2025-09-06T00:00:00Z",
  "hash": "sha256:abc123...",
  "splits": {
    "train": [...],
    "validation": [...],
    "test": [...]
  },
  "metadata": {
    "total_samples": 1000,
    "avg_question_length": 25,
    "avg_passage_length": 150
  }
}
```

## Usage

```python
from eval.datasets import load_dataset, create_split

# Load a dataset by hash
dataset = load_dataset("sha256:abc123...")

# Create deterministic splits
train, val, test = create_split(dataset, seed=42)
```

## Available Datasets

- **RAG Baseline**: Small test dataset for initial validation
- **QA Grounding**: Questions with passage citations
- **Retrieval Top-K**: Document retrieval evaluation

## Adding New Datasets

1. Generate SHA-256 hash of dataset content
2. Store large datasets out-of-repo (S3, etc.)
3. Add metadata to this README
4. Update dataset registry in `eval/datasets/registry.py`
