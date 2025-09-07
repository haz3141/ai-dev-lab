# RAG Evaluation Evidence

This directory contains evidence and results from RAG evaluation runs.

## Run-to-Evidence Policy

### Evidence Collection
- **Deterministic Runs**: All evaluations use fixed seeds for reproducibility
- **Artifact Storage**: Results, logs, and metrics are stored with timestamps
- **Version Tracking**: Each run includes dataset version and model configuration

### Evidence Format

```json
{
  "metadata": {
    "version": "1.0.0",
    "created_at": "2025-09-06T00:00:00Z",
    "seed": 42,
    "total_questions": 100
  },
  "metrics": {
    "accuracy": 0.85,
    "grounding_rate": 0.92,
    "avg_confidence": 0.78
  },
  "results": [...]
}
```

### File Naming Convention
- `results_YYYYMMDD_HHMMSS.json` - Full evaluation results
- `metrics_YYYYMMDD_HHMMSS.json` - Aggregated metrics only
- `logs_YYYYMMDD_HHMMSS.txt` - Evaluation logs

## Threshold Policies

### Accuracy Thresholds
- **Minimum**: 0.8 (80%)
- **Fail Threshold**: 0.05 (5% drop)
- **Action**: Alert if accuracy drops below threshold

### Grounding Thresholds  
- **Minimum**: 0.9 (90%)
- **Fail Threshold**: 0.10 (10% drop)
- **Action**: Alert if grounding rate drops below threshold

### Latency Thresholds
- **Maximum P95**: 2000ms
- **Fail Threshold**: 0.20 (20% increase)
- **Action**: Alert if latency increases above threshold

## Evaluation Runs

### Baseline Run (2025-09-06)
- **Dataset**: RAG Baseline v1.0.0
- **Seed**: 42
- **Results**: `results_20250906_000000.json`
- **Status**: ✅ Passed all thresholds

## Usage

```bash
# Run evaluation
python eval/pipeline/run_eval.py --dataset eval/datasets/test.json --output evidence/eval/results.json

# Check thresholds
python eval/pipeline/check_thresholds.py --results evidence/eval/results.json
```

## Monitoring

- **Automated**: CI runs evaluation on every PR
- **Manual**: Run evaluations before releases
- **Alerting**: Threshold violations trigger notifications

## Archival

- **Retention**: Keep results for 90 days
- **Compression**: Archive old results after 30 days
- **Cleanup**: Remove artifacts older than 1 year
