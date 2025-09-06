# Changelog

All notable changes to this project will be documented in this file.

## [0.6.2] - 2025-09-06

### Added
- **Coverage Gating**: Added pytest-cov with 68% threshold enforcement in CI
- **MCP Tool Promotions**: Added docs.search and vector.search tools to allowlist
- **Documentation Headers**: Enforced version headers on all docs/ files

### Changed
- **Lint Expansion**: Expanded Ruff rules scope with comprehensive configuration
- **CI Workflow**: Enhanced with coverage gating and documentation validation

### Pending
- **RAG Baseline**: Step 6 implementation (to be completed)

## [0.6.1] - 2024-12-19

### Added
- **Freeze Guard Script**: Enhanced freeze guard with GitHub event payload support for fork PRs
- **Documentation Check Script**: Precise version header validation for docs/ directory
- **Audit Log Rotation**: Added `rotate_and_compress()` function for log retention and compression
- **Cursor Configuration**: Added MCP server configuration with allowlisted tools
- **Documentation Rules**: Auto-attached rules for docs/ directory with version header requirements
- **CI Improvements**: Added pip caching and ensured eval artifacts always upload

### Changed
- **Ruff Configuration**: Streamlined to E, F, I rules only during freeze to avoid churn
- **Pre-commit Hooks**: Updated to pin Ruff v0.6.9 and removed ruff-format (defer to Black)
- **CI Workflow**: Replaced shell-based freeze guard with Python script
- **Code Formatting**: Applied Black formatting across all Python files
- **Import Organization**: Fixed import sorting across all modules

### Fixed
- **Line Length Violations**: Fixed E501 errors in lab/obs/ingest.py
- **Import Sorting**: Resolved I001 import organization issues
- **Freeze Guard Edge Cases**: Handle missing GITHUB_BASE_REF in fork PRs

### Security
- **Audit Logging**: Enhanced with compression and retention policies
- **PII Redaction**: Maintained existing security policies
- **Guardian Security**: All tool calls continue to go through security validation

### Testing
- **All Tests Passing**: 17/17 tests pass (1 integration + 16 security)
- **Linting Clean**: Ruff and Black checks pass without issues
- **MCP Server**: Syntax validation successful

### Configuration
- **pyproject.toml**: Updated Ruff rules and Black compatibility
- **.pre-commit-config.yaml**: Pinned versions and streamlined hooks
- **.cursorignore**: Added to exclude large datasets and temporary files
- **.cursor/mcp.json**: MCP server configuration with allowlisted tools
- **.cursor/rules/docs.mdc**: Documentation-specific rules

## [0.6.0] - Previous Release
- Initial release with MCP server, audit logging, and security policies
