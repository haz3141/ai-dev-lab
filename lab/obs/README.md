<!-- Version: 0.6.0 -->
# Observability Module

This module provides comprehensive logging, monitoring, and analysis capabilities for the AI Dev Lab.

## Components

### `audit.py`
Core audit logging system with JSONL output, PII redaction, and request correlation.

**Features:**
- JSONL structured logging
- Request ID correlation
- PII redaction via security module
- Performance metrics (latency tracking)
- Error logging and correlation
- User and session tracking

**Usage:**
```python
from lab.obs.audit import audit_logger

# Log a tool call
request_id = audit_logger.log_tool_call(
    tool_name="tools/summarize",
    input_data={"text": "Sample text"},
    output_data={"summary": "Generated summary"},
    start_time=start_time,
    user_id="user123",
    session_id="session456"
)
```

### `ingest.py`
Audit log analysis and metrics computation.

**Features:**
- Error rate calculation
- Latency percentile analysis (p50, p95, p99)
- Top failing tools identification
- Request volume analysis
- User activity metrics
- Markdown report generation

**Usage:**
```bash
# Analyze all logs
python lab/obs/ingest.py --path logs/ --output audit_summary.md

# Analyze specific tool
python lab/obs/ingest.py --tool "tools/summarize" --hours 48

# Using Cursor command
obs:ingest
```

## Log Schema

### Audit Event Structure
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
- **Pattern**: `logs/mcp_audit_YYYY-MM-DD.jsonl`
- **Retention**: 30 days (configurable)
- **Compression**: gzip after 7 days
- **Archival**: Move to cold storage after 90 days

## Metrics Computed

### Error Metrics
- **Error Rate**: `(error_count / total_requests) * 100`
- **Error Count by Tool**: Breakdown of errors per tool
- **Error Trends**: Error rate over time

### Performance Metrics
- **Latency p50**: 50th percentile response time
- **Latency p95**: 95th percentile response time
- **Latency p99**: 99th percentile response time
- **Average Response Time**: Mean latency across all requests

### Volume Metrics
- **Request Volume**: Requests per hour/day
- **Peak Usage**: Highest request periods
- **Growth Trends**: Request volume changes over time

### User Metrics
- **Unique Users**: Count of distinct user IDs
- **Unique Sessions**: Count of distinct session IDs
- **User Activity**: Requests per user/session
- **Session Duration**: Average session length

## Configuration

### Environment Variables
- `AUDIT_LOG_PATH`: Base path for audit logs (default: `logs/mcp_audit.jsonl`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `AUDIT_RETENTION_DAYS`: Log retention period (default: 30)

### Log Rotation
Daily rotation is handled automatically:
1. New day starts → create new log file with date suffix
2. Previous day's log → compress if older than 7 days
3. Old logs → archive after retention period

## Security Considerations

### PII Redaction
All input and output data is automatically redacted using the security module:
- Email addresses
- Phone numbers
- Credit card numbers
- Social security numbers
- Custom patterns (configurable)

### Data Retention
- Logs are retained for 30 days by default
- PII is redacted before storage
- Sensitive data is not included in analysis reports
- Logs can be purged on demand

## Monitoring & Alerting

### Key Metrics to Monitor
1. **Error Rate > 5%**: Indicates system issues
2. **Latency p95 > 1000ms**: Performance degradation
3. **Request Volume Spike**: Potential DDoS or usage surge
4. **Tool Failures**: Specific tools failing frequently

### Alert Thresholds
- Error rate: > 5% for 5 minutes
- Latency: p95 > 1000ms for 10 minutes
- Volume: > 200% of normal for 5 minutes
- Tool failures: > 10% error rate for any tool

## Troubleshooting

### Common Issues

**No events in logs:**
```bash
# Check if MCP server is running
curl http://127.0.0.1:8000/health

# Check log file permissions
ls -la logs/
```

**High error rates:**
```bash
# Analyze specific tool
python lab/obs/ingest.py --tool "tools/summarize"

# Check recent errors
python lab/obs/ingest.py --hours 1
```

**Performance issues:**
```bash
# Check latency percentiles
python lab/obs/ingest.py --hours 24

# Look for specific time periods
grep "2024-01-01T14" logs/mcp_audit_2024-01-01.jsonl
```

## Integration

### With Cursor IDE
- Use `obs:ingest` command to analyze logs
- Use `obs:audit` command to view recent events
- Reports are generated in markdown format

### With CI/CD
- Evaluation metrics are uploaded as artifacts
- Performance regression detection
- Security event monitoring

### With Monitoring Systems
- JSONL format is compatible with log aggregation
- Metrics can be exported to monitoring dashboards
- Alerts can be configured based on thresholds
