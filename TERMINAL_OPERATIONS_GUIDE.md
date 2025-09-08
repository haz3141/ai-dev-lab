# 🛠️ Terminal Operations Best Practices Guide

## Overview

This guide outlines the best practices for handling terminal operations in AI-assisted development, specifically for the v0.6.4 RAG Evaluation Gates implementation.

## 🎯 **Key Principles**

### **1. Avoid Complex Terminal Commands**
Instead of complex bash scripts, break down into simple, single-purpose commands:

```bash
# ❌ Avoid complex multi-line scripts
# ✅ Use simple, focused commands
git status
ls -la eval/
python eval/run.py --help
```

### **2. Use MCP Tools Instead of Terminal**
The MCP server provides tools that can replace many terminal operations:

```python
# Instead of terminal commands, use MCP tools:
# - search_docs: Find files and content
# - summarize: Process text output
# - run_command: Execute terminal commands safely
# - check_file: Verify file existence and properties
# - run_eval: Execute evaluations with proper error handling
# - check_gates: Validate evaluation gates
```

### **3. Implement Terminal Helper Functions**
Create simple Python scripts for complex operations with proper error handling.

## 🔧 **Enhanced MCP Server Tools**

### **New Terminal Helper Tools**

The MCP server now includes the following terminal helper tools:

#### **1. `run_command`**
- **Purpose**: Execute terminal commands safely with timeout
- **Parameters**: `command`, `timeout`, `cwd`
- **Returns**: Success status, stdout, stderr, return code
- **Safety**: Timeout protection, error handling

#### **2. `check_file`**
- **Purpose**: Check if files exist and get metadata
- **Parameters**: `filepath`
- **Returns**: Existence, file type, size, modification time
- **Safety**: Path validation, error handling

#### **3. `read_file`**
- **Purpose**: Safely read files with line limits
- **Parameters**: `filepath`, `max_lines`
- **Returns**: File content, line counts, truncation status
- **Safety**: Line limits, encoding handling

#### **4. `list_directory`**
- **Purpose**: List directory contents with limits
- **Parameters**: `directory`, `max_items`
- **Returns**: Directory items, counts, truncation status
- **Safety**: Item limits, path validation

#### **5. `run_eval`**
- **Purpose**: Execute evaluations with proper error handling
- **Parameters**: `dataset`, `output_dir`, `timeout`
- **Returns**: Evaluation results, success status
- **Safety**: File validation, timeout protection

#### **6. `check_gates`**
- **Purpose**: Validate evaluation gates using metrics
- **Parameters**: `metrics_file`
- **Returns**: Gate status, detailed results
- **Safety**: File validation, error handling

## 🚀 **Usage Examples**

### **Basic File Operations**
```bash
# Check if file exists
curl -X POST http://localhost:8000/tools/check_file \
  -H "Content-Type: application/json" \
  -d '{"filepath": "eval/run.py"}'

# Read file safely
curl -X POST http://localhost:8000/tools/read_file \
  -H "Content-Type: application/json" \
  -d '{"filepath": "eval/run.py", "max_lines": 50}'
```

### **Terminal Commands**
```bash
# Execute command safely
curl -X POST http://localhost:8000/tools/run_command \
  -H "Content-Type: application/json" \
  -d '{"command": "ls -la eval/", "timeout": 10}'
```

### **Evaluation Operations**
```bash
# Run evaluation
curl -X POST http://localhost:8000/tools/run_eval \
  -H "Content-Type: application/json" \
  -d '{"dataset": "eval/data/lab/lab_dev.jsonl", "output_dir": "eval/runs/test"}'

# Check gates
curl -X POST http://localhost:8000/tools/check_gates \
  -H "Content-Type: application/json" \
  -d '{"metrics_file": "eval/runs/test/metrics.json"}'
```

## 🔒 **Security Configuration**

### **Environment Variables**
The MCP server uses environment variables for security configuration:

```bash
export GUARDIAN_ALLOW_TOOLS="health,tools/summarize,tools/search_docs,tools/run_command,tools/check_file,tools/read_file,tools/list_directory,tools/run_eval,tools/check_gates"
```

### **Allowlist Configuration**
Update `config/mcp/allowlist.yaml`:
```yaml
version: v0.6.4
allow:
  - docs.search
  - vector.search
  - tools.search_docs
  - tools.summarize
  - tools.run_command
  - tools.check_file
  - tools.read_file
  - tools.list_directory
  - tools.run_eval
  - tools.check_gates
```

## 📋 **Verification Script**

The `verify_v0_6_4.py` script provides comprehensive verification:

```bash
python verify_v0_6_4.py
```

**Features:**
- ✅ File existence checks
- ✅ MCP tools testing
- ✅ Evaluation execution
- ✅ Gates validation
- ✅ Comprehensive reporting

## 🎉 **Current Status: READY FOR PRODUCTION**

### **✅ Completed Features**
1. **Enhanced MCP Server** - Terminal helper tools implemented
2. **Security Configuration** - Proper allowlist and environment setup
3. **Verification Script** - Comprehensive testing and validation
4. **Documentation** - Complete usage guide and best practices
5. **Testing** - All tools validated and working correctly

### **🚀 Next Steps**
1. **Deploy to Production**: The v0.6.4 implementation is ready
2. **CI/CD Integration**: Use the MCP tools in CI pipelines
3. **Monitoring**: Leverage audit logging for tool usage tracking
4. **Scaling**: Extend terminal helper tools as needed

## 🔧 **Implementation Details**

### **File Structure**
```
mcp_server/
├── tools/
│   ├── terminal_helper.py    # New terminal helper functions
│   ├── search_docs.py        # Document search
│   └── summarize.py          # Text summarization
├── server.py                 # Enhanced MCP server
└── ...

verify_v0_6_4.py              # Verification script
TERMINAL_OPERATIONS_GUIDE.md  # This guide
```

### **Key Benefits**
- ✅ **Structured Responses**: JSON-formatted results
- ✅ **Error Handling**: Comprehensive error management
- ✅ **Timeout Protection**: Prevents hanging operations
- ✅ **Security**: Allowlist-based access control
- ✅ **Audit Logging**: Complete operation tracking
- ✅ **Integration**: Seamless Cursor integration

## 📚 **Best Practices Summary**

1. **Use MCP Tools**: Prefer MCP tools over direct terminal commands
2. **Simple Commands**: Break complex operations into simple steps
3. **Error Handling**: Always implement proper error handling
4. **Security**: Use allowlists and environment variables
5. **Testing**: Verify functionality with comprehensive tests
6. **Documentation**: Maintain clear usage documentation

---

**Version**: v0.6.4  
**Last Updated**: September 8, 2025  
**Status**: Production Ready ✅
