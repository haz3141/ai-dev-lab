<!--
Version: 0.6.4
-->
# Lab to App Promotion Workflow

This document outlines the process for promoting code from the `lab/` directory to the `app/` directory, maintaining separation between experimental and production code.

## Overview

The AI Dev Lab follows a two-tier architecture:
- **Lab**: Experimental code, research, and prototypes
- **App**: Production-ready code for deployment

## Promotion Criteria

Before promoting code from lab to app, ensure:

### 1. Code Quality
- [ ] Unit tests with >80% coverage
- [ ] Integration tests passing
- [ ] Security review completed
- [ ] Performance benchmarks met
- [ ] Documentation updated

### 2. Security & Compliance
- [ ] No hardcoded secrets
- [ ] PII handling reviewed
- [ ] Input validation implemented
- [ ] Error handling secure
- [ ] Audit logging in place

### 3. Production Readiness
- [ ] Configuration externalized
- [ ] Logging structured
- [ ] Monitoring implemented
- [ ] Error recovery tested
- [ ] Scalability considered

## Promotion Process

### Step 1: Lab Stabilization
```bash
# Ensure lab code is stable
cd lab/
pytest tests/
python -m lab.eval.run_eval
```

### Step 2: Create App Structure
```bash
# Create corresponding app structure
mkdir -p app/backend/src/feature_name
mkdir -p app/frontend/src/feature_name
```

### Step 3: Code Migration
1. Copy lab code to app
2. Refactor for production patterns
3. Add production configuration
4. Implement proper error handling
5. Add monitoring and logging

### Step 4: Testing
```bash
# Run comprehensive tests
pytest app/tests/
npm test  # for frontend
```

### Step 5: Documentation
- Update API documentation
- Create deployment guides
- Update architecture diagrams

### Step 6: Deployment
- Deploy to staging environment
- Run smoke tests
- Deploy to production
- Monitor metrics

## File Structure

```
lab/                          app/
├── security/                 ├── backend/
│   ├── guardian.py    →     │   ├── src/
│   └── redact.py      →     │   │   └── security/
├── eval/                     │   │       ├── guardian.py
│   ├── metrics.py     →     │   │       └── redact.py
│   └── run_eval.py    →     │   └── tests/
├── obs/                      ├── frontend/
│   └── audit.py       →     │   └── src/
└── tests/                    │       └── monitoring/
    └── test_*.py       →     └── docs/
```

## Best Practices

1. **Never promote directly** - Always go through review
2. **Maintain separation** - Keep lab and app independent
3. **Version control** - Tag lab versions before promotion
4. **Documentation** - Update docs with each promotion
5. **Testing** - Comprehensive testing at each stage

## Rollback Plan

If promoted code causes issues:

1. **Immediate**: Revert deployment
2. **Short-term**: Fix in app and redeploy
3. **Long-term**: Improve lab testing process

## Security Considerations

- Lab code may contain experimental security features
- App code must follow security best practices
- Regular security audits required
- PII handling must be production-ready
