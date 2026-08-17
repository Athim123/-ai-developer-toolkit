#!/usr/bin/env python3
"""
Comprehensive endpoint testing script for AI Developer Toolkit API
Run this after: uvicorn app.main:app --reload
"""

import requests
import json
from typing import Optional

BASE_URL = "http://127.0.0.1:8000"
TOKEN: Optional[str] = None
PROJECT_ID: Optional[str] = None
PROMPT_ID: Optional[str] = None
RUN_ID: Optional[str] = None

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def print_test(endpoint: str, method: str, status: bool, response=None):
    """Print test result in formatted way"""
    symbol = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
    status_text = f"{GREEN}PASS{RESET}" if status else f"{RED}FAIL{RESET}"
    print(f"{symbol} {method:6} {endpoint:50} [{status_text}]")
    if not status and response:
        print(f"  Error: {response.text[:200]}")


def test_health():
    """Test health endpoint"""
    print(f"\n{CYAN}{'='*70}")
    print("1. HEALTH CHECK")
    print(f"{'='*70}{RESET}")
    
    try:
        resp = requests.get(f"{BASE_URL}/health")
        success = resp.status_code == 200
        print_test("/health", "GET", success, resp)
        return success
    except Exception as e:
        print(f"{RED}Connection error: {e}{RESET}")
        return False


def test_auth():
    """Test authentication endpoints"""
    global TOKEN
    print(f"\n{CYAN}{'='*70}")
    print("2. AUTHENTICATION")
    print(f"{'='*70}{RESET}")
    
    # Register
    register_payload = {
        "email": "testuser@example.com",
        "name": "Test User",
        "password": "TestPass123!"
    }
    try:
        resp = requests.post(f"{BASE_URL}/v1/auth/register", json=register_payload)
        success = resp.status_code in [201, 409]  # 409 if already exists
        print_test("/v1/auth/register", "POST", success, resp)
    except Exception as e:
        print(f"{RED}Register error: {e}{RESET}")
        return False
    
    # Login
    login_payload = {
        "username": "testuser@example.com",
        "password": "TestPass123!"
    }
    try:
        resp = requests.post(f"{BASE_URL}/v1/auth/login", data=login_payload)
        success = resp.status_code == 200
        if success:
            TOKEN = resp.json()["access_token"]
            print_test("/v1/auth/login", "POST", success, resp)
            print(f"  → Token obtained: {TOKEN[:20]}...")
            return True
        else:
            print_test("/v1/auth/login", "POST", False, resp)
            return False
    except Exception as e:
        print(f"{RED}Login error: {e}{RESET}")
        return False


def test_projects():
    """Test project endpoints"""
    global PROJECT_ID, TOKEN
    if not TOKEN:
        print(f"{RED}Skipping projects (no token){RESET}")
        return False
    
    print(f"\n{CYAN}{'='*70}")
    print("3. PROJECTS")
    print(f"{'='*70}{RESET}")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # Create project
    create_payload = {"name": "Test Project"}
    try:
        resp = requests.post(f"{BASE_URL}/v1/projects", json=create_payload, headers=headers)
        success = resp.status_code == 201
        if success:
            PROJECT_ID = resp.json()["id"]
            print_test("/v1/projects", "POST", success, resp)
            print(f"  → Project ID: {PROJECT_ID}")
        else:
            print_test("/v1/projects", "POST", False, resp)
            return False
    except Exception as e:
        print(f"{RED}Create project error: {e}{RESET}")
        return False
    
    # List projects
    try:
        resp = requests.get(f"{BASE_URL}/v1/projects", headers=headers)
        success = resp.status_code == 200
        print_test("/v1/projects", "GET", success, resp)
        return success
    except Exception as e:
        print(f"{RED}List projects error: {e}{RESET}")
        return False


def test_prompts():
    """Test prompt endpoints"""
    global PROMPT_ID, TOKEN, PROJECT_ID
    if not TOKEN or not PROJECT_ID:
        print(f"{RED}Skipping prompts (missing token/project){RESET}")
        return False
    
    print(f"\n{CYAN}{'='*70}")
    print("4. PROMPTS")
    print(f"{'='*70}{RESET}")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # Create prompt
    create_payload = {
        "project_id": PROJECT_ID,
        "name": "Test Prompt",
        "template": "Question: {{question}}\nAnswer: {{answer}}"
    }
    try:
        resp = requests.post(f"{BASE_URL}/v1/prompts", json=create_payload, headers=headers)
        success = resp.status_code == 201
        if success:
            PROMPT_ID = resp.json()["id"]
            print_test("/v1/prompts", "POST", success, resp)
            print(f"  → Prompt ID: {PROMPT_ID}")
        else:
            print_test("/v1/prompts", "POST", False, resp)
            return False
    except Exception as e:
        print(f"{RED}Create prompt error: {e}{RESET}")
        return False
    
    # Get prompt
    if PROMPT_ID:
        try:
            resp = requests.get(f"{BASE_URL}/v1/prompts/{PROMPT_ID}", headers=headers)
            success = resp.status_code == 200
            print_test(f"/v1/prompts/{{id}}", "GET", success, resp)
            return success
        except Exception as e:
            print(f"{RED}Get prompt error: {e}{RESET}")
            return False
    
    return False


def test_tools():
    """Test tools endpoints"""
    global TOKEN
    if not TOKEN:
        print(f"{RED}Skipping tools (no token){RESET}")
        return False
    
    print(f"\n{CYAN}{'='*70}")
    print("5. TOOLS")
    print(f"{'='*70}{RESET}")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # List tools
    try:
        resp = requests.get(f"{BASE_URL}/v1/tools", headers=headers)
        success = resp.status_code == 200
        print_test("/v1/tools", "GET", success, resp)
        tools = resp.json() if success else []
        if tools:
            print(f"  → Available tools: {[t.get('name', 'unknown') for t in tools[:3]]}")
    except Exception as e:
        print(f"{RED}List tools error: {e}{RESET}")
        return False
    
    # Execute a tool
    execute_payload = {
        "tool_name": "calculator",
        "arguments": {"operation": "add", "a": 5, "b": 3}
    }
    try:
        resp = requests.post(f"{BASE_URL}/v1/tools/execute", json=execute_payload, headers=headers)
        success = resp.status_code == 200
        print_test("/v1/tools/execute", "POST", success, resp)
        return success
    except Exception as e:
        print(f"{RED}Execute tool error: {e}{RESET}")
        return False


def test_runs():
    """Test run endpoints"""
    global RUN_ID, TOKEN, PROJECT_ID
    if not TOKEN or not PROJECT_ID:
        print(f"{RED}Skipping runs (missing token/project){RESET}")
        return False
    
    print(f"\n{CYAN}{'='*70}")
    print("6. RUNS (Workflows)")
    print(f"{'='*70}{RESET}")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # Create a run
    run_payload = {
        "project_id": PROJECT_ID,
        "workflow": "code_assist",
        "input": {"task": "Calculate 42 * 17"},
        "tools": ["calculator"]
    }
    try:
        resp = requests.post(f"{BASE_URL}/v1/runs", json=run_payload, headers=headers)
        success = resp.status_code == 201
        if success:
            RUN_ID = resp.json()["run_id"]
            print_test("/v1/runs", "POST", success, resp)
            print(f"  → Run ID: {RUN_ID}")
        else:
            print_test("/v1/runs", "POST", False, resp)
    except Exception as e:
        print(f"{RED}Create run error: {e}{RESET}")
        return False
    
    # Get run details
    if RUN_ID:
        try:
            resp = requests.get(f"{BASE_URL}/v1/runs/{RUN_ID}", headers=headers)
            success = resp.status_code == 200
            print_test(f"/v1/runs/{{run_id}}", "GET", success, resp)
        except Exception as e:
            print(f"{RED}Get run error: {e}{RESET}")
    
    # Get run trace
    if RUN_ID:
        try:
            resp = requests.get(f"{BASE_URL}/v1/runs/{RUN_ID}/trace", headers=headers)
            success = resp.status_code == 200
            print_test(f"/v1/runs/{{run_id}}/trace", "GET", success, resp)
            return success
        except Exception as e:
            print(f"{RED}Get trace error: {e}{RESET}")
            return False
    
    return False


def test_retrieval():
    """Test retrieval endpoints"""
    global TOKEN, PROJECT_ID
    if not TOKEN or not PROJECT_ID:
        print(f"{RED}Skipping retrieval (missing token/project){RESET}")
        return False
    
    print(f"\n{CYAN}{'='*70}")
    print("7. RETRIEVAL (RAG)")
    print(f"{'='*70}{RESET}")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # Index document
    doc_payload = {
        "project_id": PROJECT_ID,
        "title": "Python Programming Guide",
        "content": "This is a test document about Python programming.",
        "source": "test"
    }
    try:
        resp = requests.post(f"{BASE_URL}/v1/retrieval/documents", json=doc_payload, headers=headers)
        success = resp.status_code == 201
        print_test("/v1/retrieval/documents", "POST", success, resp)
    except Exception as e:
        print(f"{RED}Index document error: {e}{RESET}")
        return False
    
    # Query documents
    query_payload = {
        "project_id": PROJECT_ID,
        "query": "Python programming"
    }
    try:
        resp = requests.post(f"{BASE_URL}/v1/retrieval/query", json=query_payload, headers=headers)
        success = resp.status_code == 200
        print_test("/v1/retrieval/query", "POST", success, resp)
        return success
    except Exception as e:
        print(f"{RED}Query error: {e}{RESET}")
        return False


def test_evaluate():
    """Test evaluation endpoints"""
    global TOKEN, PROJECT_ID, RUN_ID
    if not TOKEN or not PROJECT_ID:
        print(f"{RED}Skipping evaluate (missing token/project){RESET}")
        return False
    
    print(f"\n{CYAN}{'='*70}")
    print("8. EVALUATION")
    print(f"{'='*70}{RESET}")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # Evaluate a run (only if we have a completed run)
    if not RUN_ID:
        print(f"{YELLOW}Skipping evaluate (no run ID available){RESET}")
        return False
    
    eval_payload = {
        "run_id": RUN_ID,
        "criteria": ["correctness", "relevance", "safety"]
    }
    try:
        resp = requests.post(f"{BASE_URL}/v1/evaluate", json=eval_payload, headers=headers)
        success = resp.status_code == 200  # Returns 200, not 201
        print_test("/v1/evaluate", "POST", success, resp)
        return success
    except Exception as e:
        print(f"{RED}Evaluate error: {e}{RESET}")
        return False


def main():
    """Run all tests"""
    print(f"\n{CYAN}╔{'='*68}╗")
    print(f"║ {'AI Developer Toolkit - API Endpoint Testing':^66} ║")
    print(f"║ {'Testing against: ' + BASE_URL:^66} ║")
    print(f"╚{'='*68}╝{RESET}\n")
    
    results = {}
    
    results["Health"] = test_health()
    results["Auth"] = test_auth()
    results["Projects"] = test_projects()
    results["Prompts"] = test_prompts()
    results["Tools"] = test_tools()
    results["Runs"] = test_runs()
    results["Retrieval"] = test_retrieval()
    results["Evaluate"] = test_evaluate()
    
    # Summary
    print(f"\n{CYAN}{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}{RESET}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, status in results.items():
        symbol = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
        print(f"{symbol} {test_name:20} {'PASS' if status else 'FAIL'}")
    
    print(f"\n{CYAN}Total: {passed}/{total} test groups passed{RESET}\n")
    
    if passed == total:
        print(f"{GREEN}All tests passed! 🎉{RESET}\n")
    else:
        print(f"{YELLOW}Some tests failed. Check output above for details.{RESET}\n")


if __name__ == "__main__":
    main()
