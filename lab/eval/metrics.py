from __future__ import annotations
from typing import List, Dict
import numpy as np

def hit_at_k(results: List[List[str]], gold: List[str], k: int = 3) -> float:
    """
    Calculate Hit@K metric for retrieval evaluation.
    
    Args:
        results: List of retrieved chunk IDs for each query
        gold: List of ground truth chunk IDs
        k: Number of top results to consider
        
    Returns:
        Hit@K score (0.0 to 1.0)
    """
    hits = 0
    for r, g in zip(results, gold):
        hits += 1 if any(g == cand for cand in r[:k]) else 0
    return hits / max(1, len(gold))

def mrr_at_k(results: List[List[str]], gold: List[str], k: int = 5) -> float:
    """
    Calculate Mean Reciprocal Rank@K metric for retrieval evaluation.
    
    Args:
        results: List of retrieved chunk IDs for each query
        gold: List of ground truth chunk IDs
        k: Number of top results to consider
        
    Returns:
        MRR@K score (0.0 to 1.0)
    """
    rr = []
    for r, g in zip(results, gold):
        try:
            rank = r[:k].index(g) + 1
            rr.append(1.0 / rank)
        except ValueError:
            rr.append(0.0)
    return float(np.mean(rr)) if rr else 0.0
