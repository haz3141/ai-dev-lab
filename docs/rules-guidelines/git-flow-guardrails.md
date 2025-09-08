<!-- Version: 0.6.4 -->

# Git Flow Guardrails - Implementation Guide

## Overview

This document describes the Git flow guardrails implemented in AI-Dev-Lab v0.6.4, combining Cursor Rules with MCP tools to enforce best practices for branching, committing, and PR creation.

## Components

### 1. Cursor Rule: `.cursor/rules/git-flow.mdc`

**Location**: `.cursor/rules/git-flow.mdc`
**Purpose**: Defines Git flow policies and guides AI behavior during development

**Key Rules**:
- Never commit to `main` or `release/*` branches
- Use feature branches: `feat/scope-desc`, `fix/scope-desc`, `chore/scope-desc`
- Conventional commits: `type(scope)!: summary`
- Pre-commit gates: tests, lint, working tree clean
- PR requirements with checklists and labels

### 2. MCP Tools: Git Guardrails

**Location**: `mcp_server/tools/git_guardrails.py`
**Purpose**: Provides executable tools to enforce Git flow rules at runtime

**Available Tools**:

#### `ensure_on_feature_branch()`
- **Purpose**: Validates current branch follows naming conventions
- **Returns**: `{ok, branch, reason}`
- **Usage**: Call before any commit operation

#### `safe_commit(type, scope, summary, breaking=False)`
- **Purpose**: Runs pre-commit checks and creates conventional commit
- **Parameters**:
  - `type`: feat, fix, docs, style, refactor, test, chore
  - `scope`: Feature area (optional)
  - `summary`: Brief description
  - `breaking`: Breaking change flag
- **Returns**: `{success, reason, commit_sha, commit_message}`

#### `create_pr(title, body, labels[])`
- **Purpose**: Creates PR with standard template and validation
- **Parameters**:
  - `title`: PR title (conventional format)
  - `body`: PR description
  - `labels`: List of labels to apply
- **Returns**: `{success, reason, pr_url, title}`

#### `branch_diff_summary(base="main")`
- **Purpose**: Summarizes changes between branches for PR descriptions
- **Returns**: `{commits_ahead, changed_files, commit_summary, base_branch}`

### 3. MCP Configuration

**Location**: `.cursor/mcp.json`
**Purpose**: Registers the Git guardrails server with Cursor

```json
{
  "mcpServers": {
    "lab-server": {
      "command": ".venv/bin/python",
      "args": ["-m", "mcp_server.simple_server"],
      "env": {}
    }
  }
}
```

### 4. Tool Allowlist

**Location**: `config/mcp/allowlist.yaml`
**Purpose**: Controls which MCP tools are permitted

Added tools:
- `tools.ensure_on_feature_branch`
- `tools.safe_commit`
- `tools.create_pr`
- `tools.branch_diff_summary`

### 5. Server-Side GitHub Workflows

**Purpose**: Enforce Git flow rules at the repository level, even when users bypass local MCP tools

#### Branch Name Validation
**Location**: `.github/workflows/branch-name.yml`
**Trigger**: PR opened/edited/synchronized/reopened
**Action**: `deepakputhraya/action-branch-name@v1`

**Configuration**:
```yaml
regex: '^(feat|fix|chore|docs|refactor|perf|test|build|ci|revert)\/[a-z0-9._-]+$'
ignore: main|release\/.+|hotfix\/.+   # adjust if you use hotfix/*
```

#### Semantic PR Title Enforcement
**Location**: `.github/workflows/semantic-pr.yml`
**Trigger**: PR opened/edited/synchronized/reopened/ready_for_review
**Action**: `amannn/action-semantic-pull-request@v5`

**Supported Types**:
- feat, fix, chore, docs, refactor, perf, test, build, ci, revert

### 6. GitHub Branch Protection Requirements

**Required Settings** for `main` and `release/*` branches:
- ✅ Require PRs for all changes
- ✅ Require status checks (map to your CI job names)
- ✅ Restrict pushes to prevent direct commits
- ✅ Require linear history (optional)
- ✅ Require signed commits (optional)

**Status Checks**: Must match your CI workflow job names exactly:
- `security-tests`
- `eval-tests`
- `integration-tests`
- `lint`
- `docs-check`

## Usage Patterns

### Daily Development Workflow

1. **Start Feature Work**:
   ```
   "Follow Git Flow rule. Call ensure_on_feature_branch() first."
   ```

2. **Make Changes & Commit**:
   ```
   "Summarize @Commit changes. If tests & lint pass, propose Conventional Commit (type/scope: message) and call safe_commit."
   ```

3. **Create PR**:
   ```
   "Draft PR to main summarizing @Branch vs main, with checklist and labels. Call create_pr()."
   ```

### Example AI Prompt

```
"Follow our Git Flow rule. First call ensure_on_feature_branch().
Summarize @Commit changes. If tests & lint pass, propose a Conventional
Commit (type/scope: message) and call safe_commit. Then draft a PR to
main summarizing @Branch vs main, with checklist and labels. If any
gate fails, stop and fix."
```

## Integration with Existing Systems

### Branch Protection
- Works with GitHub/GitLab branch protection rules
- Requires PRs for `main` branch changes
- Enforces status checks (CI, security, etc.)
- **New**: Server-side validation via GitHub workflows

### Pre-commit Hooks
- Integrates with existing pre-commit configurations
- Runs tests, linting, and formatting checks
- Validates conventional commit format

### CI/CD Pipeline
- Leverages existing CI gates (test coverage ≥68%)
- Enforces commit message format via commitlint
- Black formatting validation

### Server-Side Enforcement
- **Branch Name Validation**: GitHub workflow validates PR branch names
- **Semantic PR Titles**: GitHub workflow enforces conventional commit format in PR titles
- **Backup Protection**: Catches policy violations even when users bypass local MCP tools

## Security Considerations

### Tool Validation
- All Git operations validate branch context
- Pre-commit checks prevent unsafe commits
- MCP allowlist controls tool access

### Audit Trail
- All Git operations are logged
- Commit messages include change rationale
- PR creation includes comprehensive checklists

## Error Handling

### Branch Validation Failures
- On `main` branch: Suggests creating feature branch
- Invalid branch name: Provides naming examples
- Not in git repo: Returns appropriate error

### Pre-commit Check Failures
- Working tree dirty: Suggests staging changes
- Tests failing: Provides test output details
- Lint issues: Shows formatting problems

### PR Creation Failures
- Branch not ahead: No commits to create PR from
- GitHub CLI not available: Falls back to manual PR creation
- Invalid title format: Validates conventional commit format

## Testing the Integration

### Manual Testing Steps

1. **Test Branch Validation**:
   ```bash
   # On main branch
   cursor-agent "Call ensure_on_feature_branch()"
   # Should return: ok=false, reason="Cannot commit to protected branch"
   ```

2. **Test Safe Commit**:
   ```bash
   # On feature branch with changes
   cursor-agent "Call safe_commit('feat', 'git-tools', 'add Git flow guardrails')"
   # Should run checks and create commit
   ```

3. **Test PR Creation**:
   ```bash
   cursor-agent "Call create_pr('feat(git-tools): add Git flow guardrails', 'Implements Git flow enforcement...', ['type/feature', 'area/dev-tools'])"
   ```

### Automated Testing
- Unit tests for Git tool functions
- Integration tests with mock git repository
- End-to-end workflow testing

## Troubleshooting

### Common Issues

1. **MCP Tools Not Available**
   - Check `.cursor/mcp.json` configuration
   - Verify server is running: `python -m mcp_server.simple_server`
   - Check allowlist includes new tools

2. **Git Commands Failing**
   - Ensure git repository is initialized
   - Check git configuration (user.name, user.email)
   - Verify GitHub CLI is installed for PR creation

3. **Pre-commit Checks Failing**
   - Install required tools: `pip install black pytest`
   - Configure pre-commit hooks if needed
   - Check test configuration and dependencies

### Debug Commands

```bash
# Check MCP server status
curl -s http://127.0.0.1:8765/health

# Test Git tool directly
python -c "from mcp_server.tools.git_guardrails import ensure_on_feature_branch; print(ensure_on_feature_branch())"

# Check current branch
git branch --show-current
```

## Future Enhancements

### Planned Features
- Interactive branch creation workflow
- PR template customization
- Integration with issue tracking systems
- Advanced commit message suggestions
- Branch cleanup automation

### Configuration Options
- Custom branch naming patterns
- Configurable pre-commit check suites
- Organization-specific PR templates
- Integration with external CI systems

## Cross-references

- **Architecture**: See `docs/architecture/promotion-lab-to-app.md`
- **Security**: See `docs/rules-guidelines/security-compliance-checklist.md`
- **MCP Tools**: See `docs/mcp/tools/` directory
- **Cursor Usage**: See `docs/cursor-usage.md`

## Version History

- **v0.6.4**: Complete Git flow guardrails implementation
  - Added Cursor rule for Git flow policies
  - Implemented MCP tools for enforcement
  - Integrated with existing MCP server architecture
  - Added comprehensive allowlist validation
  - **Added server-side GitHub workflows** for branch name and semantic PR validation
  - **Added GitHub branch protection requirements** documentation
  - **Enhanced dual entrypoint documentation** (Cursor stdio vs Docker HTTP)
