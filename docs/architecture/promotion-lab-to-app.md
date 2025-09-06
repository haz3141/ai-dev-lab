# Lab to App Promotion Flow

This document describes the process for promoting features from the `lab/` directory to the `app/` directory for production use.

## Overview

The `lab/` directory serves as a sandbox for experimental AI features, while `app/` contains production-ready code. This promotion flow ensures that only well-tested, secure, and performant features make it to production.

## Promotion Criteria

### 1. Testing Requirements
- [ ] Unit tests with >90% coverage
- [ ] Integration tests for all endpoints
- [ ] Security tests (Guardian, redaction)
- [ ] Performance benchmarks
- [ ] Evaluation metrics meet thresholds (hit@k > 0.7, mrr@k > 0.5)

### 2. Security Review
- [ ] Guardian allowlist configured
- [ ] PII redaction enabled
- [ ] Audit logging implemented
- [ ] No hardcoded secrets or credentials
- [ ] Input validation and sanitization

### 3. Documentation
- [ ] API documentation complete
- [ ] Configuration options documented
- [ ] Error handling documented
- [ ] Performance characteristics documented

### 4. Code Quality
- [ ] Code review completed
- [ ] Linting passes
- [ ] Type hints complete
- [ ] Error handling comprehensive
- [ ] Logging appropriate

## Promotion Steps

### Step 1: Lab Development
1. Develop feature in `lab/` directory
2. Add comprehensive tests
3. Implement security measures (Guardian, redaction)
4. Add audit logging
5. Document thoroughly

### Step 2: Internal Review
1. Run full test suite
2. Security review checklist
3. Performance evaluation
4. Code review
5. Documentation review

### Step 3: Staging Deployment
1. Copy module to `app/` directory
2. Adapt for production environment
3. Add production configuration
4. Deploy to staging environment
5. Run integration tests

### Step 4: Production Rollout
1. Feature flag implementation
2. Gradual rollout (10% → 50% → 100%)
3. Monitor metrics and logs
4. Rollback plan ready
5. Full deployment

## Security Considerations

### Guardian Configuration
- Default deny policy with explicit allowlist
- PII redaction enabled by default
- Tool-specific policies as needed

### Audit Logging
- All tool calls logged
- Request/response sanitization
- Correlation IDs for tracing
- Log retention policies

### Data Protection
- No PII in logs
- Encrypted data at rest
- Secure communication channels
- Access controls

## Monitoring and Alerting

### Key Metrics
- Request latency (p95, p99)
- Error rates
- Security violations
- Resource usage

### Alerts
- High error rates (>5%)
- Security violations
- Performance degradation
- Resource exhaustion

## Rollback Procedures

### Immediate Rollback
1. Disable feature flag
2. Revert to previous version
3. Monitor for issues
4. Investigate root cause

### Gradual Rollback
1. Reduce traffic percentage
2. Monitor metrics
3. Identify affected users
4. Plan full rollback if needed

## Best Practices

1. **Start Small**: Begin with low-risk features
2. **Monitor Closely**: Watch metrics during rollout
3. **Test Thoroughly**: Comprehensive testing before promotion
4. **Document Everything**: Keep detailed records
5. **Plan for Failure**: Always have rollback plans
6. **Security First**: Security review is mandatory
7. **Performance Matters**: Meet performance thresholds
8. **User Impact**: Consider user experience

## Checklist Template

Use this checklist for each promotion:

- [ ] Feature complete in lab/
- [ ] Tests written and passing
- [ ] Security review completed
- [ ] Performance evaluation done
- [ ] Documentation updated
- [ ] Code review completed
- [ ] Staging deployment successful
- [ ] Production rollout planned
- [ ] Monitoring configured
- [ ] Rollback plan ready
