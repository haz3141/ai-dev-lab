<!--
Version: 0.6.4
-->
# Folder-by-Folder Audit Plan

This document outlines the systematic audit process for the AI Dev Lab project during the code freeze phase.

## Audit Scope & Order

### 1. Top-level & Environment
- [ ] `README.md` - Project overview, quick start, architecture
- [ ] `CHANGELOG.md` - Version history and changes
- [ ] `VERSION` - Current version tracking
- [ ] `.env.sample` - Environment variable template

### 2. Configuration Files
- [ ] `.cursor/**` - Cursor IDE configuration
- [ ] `.github/**` - CI/CD workflows and templates
- [ ] `pyproject.toml` - Python project configuration
- [ ] `requirements.txt` - Python dependencies
- [ ] `package.json` - Node.js dependencies (if any)

### 3. MCP Server (`mcp-server/`)
- [ ] `server.py` - FastAPI endpoints and tool definitions
- [ ] Guardian allowlist configuration
- [ ] PII redaction implementation
- [ ] Logging schema and request correlation
- [ ] Error handling and response formats

### 4. Lab Evaluation (`lab/eval/`)
- [ ] `dataset.jsonl` - Evaluation dataset structure
- [ ] `metrics.py` - Evaluation metrics and calculations
- [ ] `run_eval.py` - Evaluation harness and execution
- [ ] Test coverage and deterministic results

### 5. Lab Observability (`lab/obs/`)
- [ ] `audit.py` - JSONL audit logging system
- [ ] `ingest.py` - Log ingestion and analysis utilities
- [ ] Daily rotation and retention policies
- [ ] Performance metrics (p50/p95, error rates)

### 6. Lab Security (`lab/security/`)
- [ ] `guardian.py` - Access control and policy enforcement
- [ ] `redact.py` - PII redaction implementation
- [ ] `tests/` - Security test coverage
- [ ] Policy configuration and allowlists

### 7. Lab DSP (`lab/dsp/`)
- [ ] `summarize.py` - Text summarization implementation
- [ ] `demo_summarize.py` - Demo and examples
- [ ] Model configuration and parameters

### 8. App Structure (`app/`)
- [ ] `backend/` - Backend service interfaces
- [ ] `frontend/` - Frontend application interfaces
- [ ] `mcp-servers/` - MCP server configurations
- [ ] Interface definitions only (no behavior changes during freeze)

### 9. Documentation (`docs/`)
- [ ] `architecture/` - System architecture and workflows
- [ ] `rules-guidelines/` - Development guidelines and checklists
- [ ] `setup/` - Setup and installation guides
- [ ] `research/` - Research notes and findings

## Audit Checklist (per folder/file)

### Ownership & Purpose
- [ ] Clear 1-liner description in README or folder README
- [ ] Purpose and responsibility defined
- [ ] Dependencies and relationships documented

### Public API Surface
- [ ] Docstrings present for all public functions/classes
- [ ] Type hints for all parameters and return values
- [ ] Examples and usage patterns documented
- [ ] API versioning strategy (if applicable)

### Logging & Observability
- [ ] Request ID correlation across all operations
- [ ] Status codes and error handling
- [ ] Latency tracking and performance metrics
- [ ] PII redaction on all outputs
- [ ] Structured logging format (JSON)

### Testing
- [ ] Unit tests present and passing
- [ ] Integration tests for external dependencies
- [ ] Test coverage >80% for critical paths
- [ ] Deterministic test results (no flaky tests)
- [ ] Security tests for sensitive operations

### CI Coverage
- [ ] Lint checks (ruff, black)
- [ ] Security scans (bandit, detect-secrets)
- [ ] Test execution (pytest)
- [ ] Evaluation runs (for AI/ML components)
- [ ] Documentation checks

### Documentation
- [ ] Version headers present (`<!-- Version: 0.6.0 -->`)
- [ ] API documentation current
- [ ] Architecture diagrams updated
- [ ] Setup and deployment guides
- [ ] Troubleshooting and FAQ

### Cursor Integration
- [ ] Indexing picks up all relevant files
- [ ] Rules apply to all code paths
- [ ] Commands work for all components
- [ ] MCP tools accessible where needed

## JSONL Audit Schema

### Locked Schema Fields
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "uuid4-string",
  "event_type": "tool_call|security_event|system_event",
  "tool_name": "tools/summarize|tools/search_docs|etc",
  "input_data": "sanitized-input-object",
  "output_data": "sanitized-output-object",
  "user_id": "optional-user-identifier",
  "session_id": "optional-session-identifier",
  "duration_ms": 123.45,
  "error": "optional-error-message"
}
```

### Daily Rotation
- Log files: `logs/mcp_audit_YYYY-MM-DD.jsonl`
- Retention: 30 days (configurable)
- Compression: gzip after 7 days
- Archival: Move to cold storage after 90 days

## Ingest Utilities

### `lab/obs/ingest.py`
- Parse JSONL audit logs
- Compute error rates by tool
- Calculate p50/p95 latency percentiles
- Identify top failing tools
- Generate summary reports

### Metrics Computed
- **Error Rate**: `(error_count / total_requests) * 100`
- **Latency p50**: 50th percentile response time
- **Latency p95**: 95th percentile response time
- **Top Failing Tools**: Tools with highest error rates
- **Request Volume**: Requests per hour/day
- **User Activity**: Unique users and sessions

## Audit Execution

### Phase 1: Infrastructure (Days 1-2)
1. Top-level files and configuration
2. CI/CD setup and validation
3. Cursor configuration verification

### Phase 2: Core Services (Days 3-4)
1. MCP server audit
2. Security system review
3. Audit logging validation

### Phase 3: Lab Components (Days 5-6)
1. Evaluation system audit
2. Observability tools review
3. DSP components check

### Phase 4: Documentation (Day 7)
1. All documentation review
2. Version header verification
3. Link and reference validation

## Success Criteria

### Technical
- [ ] All tests passing
- [ ] No linting errors
- [ ] Security scans clean
- [ ] Documentation complete and current
- [ ] Performance metrics within acceptable ranges

### Process
- [ ] Code freeze respected (no logic changes)
- [ ] All changes properly documented
- [ ] CI/CD pipeline functional
- [ ] Cursor integration working

### Quality
- [ ] API documentation complete
- [ ] Examples and usage patterns clear
- [ ] Error handling comprehensive
- [ ] Logging and monitoring adequate

## Deliverables

1. **Audit Report**: Summary of findings and recommendations
2. **Updated Documentation**: All docs with version headers and current info
3. **Performance Baseline**: Current metrics and benchmarks
4. **Security Review**: Security posture and recommendations
5. **CI/CD Validation**: Pipeline health and coverage
6. **Cursor Integration**: Configuration and tool access verification

## Next Steps After Audit

1. **Unfreeze Code**: Remove code freeze restrictions
2. **Implement Fixes**: Address any issues found during audit
3. **Update Processes**: Refine development workflows
4. **Scale Usage**: Enable broader Cursor Agent usage
5. **Monitor Metrics**: Track improvements and regressions
