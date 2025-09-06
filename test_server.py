#!/usr/bin/env python3
"""Test script to verify MCP server imports and basic functionality."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the server module
    import importlib.util
    spec = importlib.util.spec_from_file_location("mcp_server", "mcp-server/server.py")
    mcp_server = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mcp_server)
    
    print("✓ MCP server imports successfully")
    
    # Test basic functionality
    from lab.security.guardian import guardian
    from lab.obs.audit import audit_logger
    from lab.eval.metrics import evaluator
    
    print("✓ Security guardian loaded")
    print("✓ Audit logger loaded") 
    print("✓ Evaluation metrics loaded")
    
    # Test guardian functionality
    assert guardian.is_tool_allowed("health") == True
    assert guardian.is_tool_allowed("unauthorized_tool") == False
    print("✓ Guardian allowlist working")
    
    # Test audit logger
    request_id = audit_logger.log_tool_call(
        "test_tool",
        {"input": "test"},
        {"output": "test"},
        user_id="test_user"
    )
    assert request_id is not None
    print("✓ Audit logging working")
    
    # Test evaluation
    evaluator.add_result("test query", ["doc1", "doc2"], ["doc1"])
    metrics = evaluator.evaluate_all()
    assert len(metrics.hit_at_k) > 0
    print("✓ Evaluation metrics working")
    
    print("\n🎉 All Step 7 features working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
