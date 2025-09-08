#!/usr/bin/env python3
"""Simple verification script for v0.6.4 RAG Evaluation Gates"""

import os
import subprocess
import sys


def check_required_files():
    """Check if all required files exist."""
    print("🔍 Checking required files...")

    required_files = [
        "eval/run.py",
        "eval/configs/lab.yaml",
        "scripts/ci/parse_metrics.py",
        ".github/workflows/rag-gates.yml",
        "mcp_server/tools/terminal_helper.py",
    ]

    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)

    if missing_files:
        print(f"\n❌ Missing required files: {missing_files}")
        return False

    print("✅ All required files present")
    return True


def run_evaluation():
    """Run the evaluation test."""
    print("\n🚀 Running evaluation...")

    try:
        result = subprocess.run(
            [
                "python",
                "eval/run.py",
                "--dataset",
                "eval/data/lab/lab_dev.jsonl",
                "--output",
                "eval/runs/verify",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            print("✅ Evaluation completed successfully")
            print(f"Output: {result.stdout}")
            return True
        else:
            print(f"❌ Evaluation failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Evaluation timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Evaluation error: {e}")
        return False


def check_gates():
    """Check if gates pass."""
    print("\n🚪 Checking gates...")

    metrics_file = "eval/runs/verify/metrics.json"
    if not os.path.exists(metrics_file):
        print(f"❌ Metrics file not found: {metrics_file}")
        return False

    try:
        result = subprocess.run(
            [
                "python",
                "scripts/ci/parse_metrics.py",
                metrics_file,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            print("✅ All gates passed")
            print(f"Output: {result.stdout}")
            return True
        else:
            print(f"❌ Gates failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Gate check timed out")
        return False
    except Exception as e:
        print(f"❌ Gate check error: {e}")
        return False


def test_mcp_tools():
    """Test MCP tools functionality."""
    print("\n🔧 Testing MCP tools...")

    try:
        # Test terminal helper
        from mcp_server.tools.terminal_helper import (
            check_file_exists,
            list_directory_safe,
            read_file_safe,
            run_command,
        )

        # Test file check
        result = check_file_exists("eval/run.py")
        if result["exists"]:
            print("✅ MCP file check working")
        else:
            print("❌ MCP file check failed")
            return False

        # Test command execution
        result = run_command("ls -la eval/", timeout=10)
        if result["success"]:
            print("✅ MCP command execution working")
        else:
            print("❌ MCP command execution failed")
            return False

        # Test file reading
        result = read_file_safe("eval/run.py", max_lines=5)
        if result["success"] and "content" in result:
            print("✅ MCP file reading working")
        else:
            print("❌ MCP file reading failed")
            return False

        # Test directory listing
        result = list_directory_safe("eval/", max_items=5)
        if result["success"] and "items" in result:
            print("✅ MCP directory listing working")
        else:
            print("❌ MCP directory listing failed")
            return False

        print("✅ MCP tools working correctly")
        return True

    except Exception as e:
        print(f"❌ MCP tools test failed: {e}")
        return False


def test_mcp_endpoints():
    """Test MCP server endpoints."""
    print("\n🌐 Testing MCP server endpoints...")

    try:
        import subprocess
        import time

        import requests

        # Start MCP server
        print("Starting MCP server...")
        server_process = subprocess.Popen(
            [
                "python",
                "-m",
                "uvicorn",
                "mcp_server.server:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for server to start
        time.sleep(5)

        base_url = "http://localhost:8000"

        # Test health endpoint
        try:
            response = requests.get(f"{base_url}/health", timeout=10)
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
            return False

        # Test terminal endpoints
        terminal_tests = [
            ("/tools/run_command", {"command": "ls -la", "timeout": 10}),
            ("/tools/check_file", {"filepath": "eval/run.py"}),
            ("/tools/read_file", {"filepath": "eval/run.py", "max_lines": 5}),
            ("/tools/list_directory", {"directory": "eval/", "max_items": 5}),
        ]

        for endpoint, data in terminal_tests:
            try:
                response = requests.post(
                    f"{base_url}{endpoint}",
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=30,
                )
                if response.status_code == 200:
                    print(f"✅ {endpoint} working")
                else:
                    print(f"❌ {endpoint} failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
            except Exception as e:
                print(f"❌ {endpoint} error: {e}")
                return False

        # Test evaluation endpoints
        eval_tests = [
            (
                "/tools/run_eval",
                {
                    "dataset": "eval/data/lab/lab_dev.jsonl",
                    "output_dir": "eval/runs/verify",
                    "timeout": 60,
                },
            ),
            (
                "/tools/check_gates",
                {
                    "metrics_file": "eval/runs/verify/metrics.json",
                },
            ),
        ]

        for endpoint, data in eval_tests:
            try:
                response = requests.post(
                    f"{base_url}{endpoint}",
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=120,
                )
                if response.status_code == 200:
                    print(f"✅ {endpoint} working")
                else:
                    print(f"❌ {endpoint} failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
            except Exception as e:
                print(f"❌ {endpoint} error: {e}")
                return False

        # Stop server
        server_process.terminate()
        server_process.wait()

        print("✅ All MCP endpoints working correctly")
        return True

    except Exception as e:
        print(f"❌ MCP endpoints test failed: {e}")
        # Try to stop server if it's still running
        try:
            server_process.terminate()
            server_process.wait()
        except Exception:
            pass
        return False


def main():
    """Main verification function."""
    print("🎯 Verifying v0.6.4 RAG Evaluation Gates...")
    print("=" * 50)

    # Check files
    if not check_required_files():
        print("\n❌ File check failed - cannot proceed")
        sys.exit(1)

    # Test MCP tools
    if not test_mcp_tools():
        print("\n❌ MCP tools test failed - cannot proceed")
        sys.exit(1)

    # Test MCP endpoints
    if not test_mcp_endpoints():
        print("\n❌ MCP endpoints test failed - cannot proceed")
        sys.exit(1)

    # Run evaluation
    if not run_evaluation():
        print("\n❌ Evaluation failed - cannot proceed")
        sys.exit(1)

    # Check gates
    if not check_gates():
        print("\n❌ Gates failed - cannot proceed")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("🎉 v0.6.4 verification complete - READY FOR PRODUCTION!")
    print("\nNext steps:")
    print("1. git add .")
    print("2. git commit -m 'feat: v0.6.4 RAG evaluation gates'")
    print("3. git push origin feat/v0.6.4-rag-gates")
    print("4. Create PR on GitHub")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
