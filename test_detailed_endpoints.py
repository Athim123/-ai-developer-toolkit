#!/usr/bin/env python3
"""
Detailed endpoint testing for AI Developer Toolkit API
Tests edge cases, error scenarios, and response validation
"""

import requests
import json
import uuid
from typing import Optional, Dict, Any

BASE_URL = "http://127.0.0.1:8000"
TOKEN: Optional[str] = None
PROJECT_ID: Optional[str] = None
PROMPT_ID: Optional[str] = None
RUN_ID: Optional[str] = None
USER_ID: Optional[str] = None

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"


def log_test(name: str, method: str, endpoint: str, status_code: int, expected: int, response: Dict = None):
    """Log test result with details"""
    passed = status_code == expected
    symbol = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
    
    print(f"\n{symbol} {name}")
    print(f"  {method:6} {endpoint:50} {status_code} (expected {expected})")
    
    if not passed:
        print(f"  {RED}FAILED{RESET}")
        if response:
            print(f"  Response: {json.dumps(response, indent=2)[:200]}")
    else:
        if response and any(k in response for k in ['id', 'run_id', 'access_token', 'scores']):
            print(f"  {BLUE}Response keys: {list(response.keys())}{RESET}")
    
    return passed


def section(title: str):
    """Print section header"""
    print(f"\n{CYAN}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{RESET}")


# ============================================================================
# AUTH TESTS
# ============================================================================

def test_auth_detailed():
    """Detailed auth endpoint testing"""
    global TOKEN, USER_ID
    section("AUTH ENDPOINTS - Detailed Tests")
    
    results = []
    
    # Test 1: Register with valid data
    print(f"\n{BLUE}[Test Group: Registration]{RESET}")
    unique_email = f"alice_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "email": unique_email,
        "name": "Alice Developer",
        "password": "SecurePass123!"
    }
    resp = requests.post(f"{BASE_URL}/v1/auth/register", json=payload)
    result = resp.json() if resp.status_code == 201 else {}
    results.append(log_test("Register: Valid credentials", "POST", "/v1/auth/register", resp.status_code, 201, result))
    if resp.status_code == 201:
        USER_ID = result.get("id")
        print(f"  → User ID: {USER_ID}")
    
    # Test 2: Register duplicate email (should fail)
    print(f"\n{BLUE}[Test Group: Duplicate Registration]{RESET}")
    resp = requests.post(f"{BASE_URL}/v1/auth/register", json=payload)
    result = resp.json() if resp.status_code != 201 else {}
    results.append(log_test("Register: Duplicate email (conflict)", "POST", "/v1/auth/register", resp.status_code, 409, result))
    
    # Test 3: Invalid email format
    print(f"\n{BLUE}[Test Group: Validation]{RESET}")
    invalid_payload = {
        "email": "not-an-email",
        "name": "Bob",
        "password": "Pass123!"
    }
    resp = requests.post(f"{BASE_URL}/v1/auth/register", json=invalid_payload)
    results.append(log_test("Register: Invalid email format", "POST", "/v1/auth/register", resp.status_code, 400))
    
    # Test 4: Login with correct credentials
    print(f"\n{BLUE}[Test Group: Login]{RESET}")
    login_data = {
        "username": payload["email"],
        "password": "SecurePass123!"
    }
    resp = requests.post(f"{BASE_URL}/v1/auth/login", data=login_data)
    result = resp.json() if resp.status_code == 200 else {}
    results.append(log_test("Login: Correct credentials", "POST", "/v1/auth/login", resp.status_code, 200, result))
    if resp.status_code == 200:
        TOKEN = result.get("access_token")
        print(f"  → Token: {TOKEN[:30]}...")
    
    # Test 5: Login with wrong password
    wrong_login = {
        "username": payload["email"],
        "password": "WrongPassword"
    }
    resp = requests.post(f"{BASE_URL}/v1/auth/login", data=wrong_login)
    results.append(log_test("Login: Wrong password", "POST", "/v1/auth/login", resp.status_code, 401))
    
    # Test 6: Login with nonexistent user
    resp = requests.post(f"{BASE_URL}/v1/auth/login", data={"username": "nouser@example.com", "password": "pass"})
    results.append(log_test("Login: Nonexistent user", "POST", "/v1/auth/login", resp.status_code, 401))
    
    return all(results)


# ============================================================================
# PROJECT TESTS
# ============================================================================

def test_projects_detailed():
    """Detailed project endpoint testing"""
    global TOKEN, PROJECT_ID
    if not TOKEN:
        print(f"{RED}Skipping projects (no token){RESET}")
        return False
    
    section("PROJECT ENDPOINTS - Detailed Tests")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    results = []
    
    # Test 1: Create project with valid data
    print(f"\n{BLUE}[Test Group: Project Creation]{RESET}")
    payload = {"name": "ML Pipeline Project"}
    resp = requests.post(f"{BASE_URL}/v1/projects", json=payload, headers=headers)
    result = resp.json() if resp.status_code == 201 else {}
    results.append(log_test("Create: Valid project", "POST", "/v1/projects", resp.status_code, 201, result))
    if resp.status_code == 201:
        PROJECT_ID = result.get("id")
        print(f"  → Project ID: {PROJECT_ID}")
    
    # Test 2: Create another project
    print(f"\n{BLUE}[Test Group: Multiple Projects]{RESET}")
    payload2 = {"name": "Data Science Experiments"}
    resp = requests.post(f"{BASE_URL}/v1/projects", json=payload2, headers=headers)
    result = resp.json() if resp.status_code == 201 else {}
    results.append(log_test("Create: Second project", "POST", "/v1/projects", resp.status_code, 201, result))
    
    # Test 3: List projects
    print(f"\n{BLUE}[Test Group: Listing]{RESET}")
    resp = requests.get(f"{BASE_URL}/v1/projects", headers=headers)
    result = resp.json() if resp.status_code == 200 else {}
    results.append(log_test("List: User projects", "GET", "/v1/projects", resp.status_code, 200, {"count": len(result)}))
    print(f"  → Found {len(result)} projects")
    
    # Test 4: List projects without auth (should fail)
    print(f"\n{BLUE}[Test Group: Authentication]{RESET}")
    resp = requests.get(f"{BASE_URL}/v1/projects")
    results.append(log_test("List: Without auth token", "GET", "/v1/projects", resp.status_code, 401))
    
    return all(results)


# ============================================================================
# PROMPT TESTS
# ============================================================================

def test_prompts_detailed():
    """Detailed prompt endpoint testing"""
    global TOKEN, PROJECT_ID, PROMPT_ID
    if not TOKEN or not PROJECT_ID:
        print(f"{RED}Skipping prompts (missing token/project){RESET}")
        return False
    
    section("PROMPT ENDPOINTS - Detailed Tests")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    results = []
    
    # Test 1: Create prompt v1
    print(f"\n{BLUE}[Test Group: Prompt Creation]{RESET}")
    payload = {
        "project_id": PROJECT_ID,
        "name": "code_reviewer",
        "template": "Review this code:\n{code}\n\nProvide feedback."
    }
    resp = requests.post(f"{BASE_URL}/v1/prompts", json=payload, headers=headers)
    result = resp.json() if resp.status_code == 201 else {}
    results.append(log_test("Create: Prompt v1", "POST", "/v1/prompts", resp.status_code, 201, result))
    if resp.status_code == 201:
        PROMPT_ID = result.get("id")
        print(f"  → Prompt ID: {PROMPT_ID}, Version: {result.get('version', 'N/A')}")
    
    # Test 2: Create prompt v2 (versioning)
    print(f"\n{BLUE}[Test Group: Prompt Versioning]{RESET}")
    payload["template"] = "Code Review:\n{code}\n\nDetailed feedback:\n{feedback}"
    resp = requests.post(f"{BASE_URL}/v1/prompts", json=payload, headers=headers)
    result = resp.json() if resp.status_code == 201 else {}
    results.append(log_test("Create: Prompt v2 (new version)", "POST", "/v1/prompts", resp.status_code, 201, result))
    if resp.status_code == 201:
        print(f"  → New version: {result.get('version', 'N/A')}")
    
    # Test 3: Get specific prompt
    print(f"\n{BLUE}[Test Group: Prompt Retrieval]{RESET}")
    if PROMPT_ID:
        resp = requests.get(f"{BASE_URL}/v1/prompts/{PROMPT_ID}", headers=headers)
        result = resp.json() if resp.status_code == 200 else {}
        results.append(log_test("Get: Specific prompt", "GET", f"/v1/prompts/{PROMPT_ID}", resp.status_code, 200, result))
    
    # Test 4: Get nonexistent prompt
    resp = requests.get(f"{BASE_URL}/v1/prompts/nonexistent_id", headers=headers)
    results.append(log_test("Get: Nonexistent prompt", "GET", "/v1/prompts/{id}", resp.status_code, 404))
    
    # Test 5: Missing required field
    print(f"\n{BLUE}[Test Group: Validation]{RESET}")
    bad_payload = {
        "project_id": PROJECT_ID,
        "name": "bad_prompt"
        # missing 'template'
    }
    resp = requests.post(f"{BASE_URL}/v1/prompts", json=bad_payload, headers=headers)
    results.append(log_test("Create: Missing template", "POST", "/v1/prompts", resp.status_code, 400))
    
    return all(results)


# ============================================================================
# TOOLS TESTS
# ============================================================================

def test_tools_detailed():
    """Detailed tools endpoint testing"""
    global TOKEN
    if not TOKEN:
        print(f"{RED}Skipping tools (no token){RESET}")
        return False
    
    section("TOOLS ENDPOINTS - Detailed Tests")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    results = []
    
    # Test 1: List available tools
    print(f"\n{BLUE}[Test Group: Tool Discovery]{RESET}")
    resp = requests.get(f"{BASE_URL}/v1/tools", headers=headers)
    result = resp.json() if resp.status_code == 200 else {}
    results.append(log_test("List: Available tools", "GET", "/v1/tools", resp.status_code, 200, {"count": len(result) if isinstance(result, list) else 0}))
    
    tools_available = isinstance(result, list) and len(result) > 0
    if tools_available:
        print(f"  → Available tools: {len(result)}")
        if result:
            print(f"     First tool: {result[0]}")
    
    # Test 2: Execute calculator tool
    print(f"\n{BLUE}[Test Group: Tool Execution]{RESET}")
    exec_payload = {
        "tool_name": "calculator",
        "arguments": {"operation": "add", "a": 10, "b": 5}
    }
    resp = requests.post(f"{BASE_URL}/v1/tools/execute", json=exec_payload, headers=headers)
    result = resp.json() if resp.status_code == 200 else {}
    results.append(log_test("Execute: Calculator (add)", "POST", "/v1/tools/execute", resp.status_code, 200, result))
    
    # Test 3: Execute calculator with different operation
    exec_payload["arguments"] = {"operation": "multiply", "a": 6, "b": 7}
    resp = requests.post(f"{BASE_URL}/v1/tools/execute", json=exec_payload, headers=headers)
    result = resp.json() if resp.status_code == 200 else {}
    results.append(log_test("Execute: Calculator (multiply)", "POST", "/v1/tools/execute", resp.status_code, 200, result))
    
    # Test 4: Execute nonexistent tool
    print(f"\n{BLUE}[Test Group: Error Handling]{RESET}")
    bad_exec = {
        "tool_name": "nonexistent_tool",
        "arguments": {}
    }
    resp = requests.post(f"{BASE_URL}/v1/tools/execute", json=bad_exec, headers=headers)
    results.append(log_test("Execute: Nonexistent tool", "POST", "/v1/tools/execute", resp.status_code, 404))
    
    # Test 5: Without auth
    resp = requests.get(f"{BASE_URL}/v1/tools")
    results.append(log_test("List: Without auth", "GET", "/v1/tools", resp.status_code, 200))
    
    return all(results)


# ============================================================================
# RUN TESTS
# ============================================================================

def test_runs_detailed():
    """Detailed run endpoint testing"""
    global TOKEN, PROJECT_ID, RUN_ID
    if not TOKEN or not PROJECT_ID:
        print(f"{RED}Skipping runs (missing token/project){RESET}")
        return False
    
    section("RUN ENDPOINTS - Detailed Tests")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    results = []
    
    # Test 1: Create basic run
    print(f"\n{BLUE}[Test Group: Run Creation]{RESET}")
    payload = {
        "project_id": PROJECT_ID,
        "workflow": "code_assist",
        "input": {"task": "Calculate 100 + 50"},
        "tools": ["calculator"]
    }
    resp = requests.post(f"{BASE_URL}/v1/runs", json=payload, headers=headers)
    result = resp.json() if resp.status_code == 201 else {}
    results.append(log_test("Create: Basic run", "POST", "/v1/runs", resp.status_code, 201, result))
    if resp.status_code == 201:
        RUN_ID = result.get("run_id")
        print(f"  → Run ID: {RUN_ID}, Status: {result.get('status')}")
    
    # Test 2: Create run with model override
    print(f"\n{BLUE}[Test Group: Advanced Parameters]{RESET}")
    payload2 = {
        "project_id": PROJECT_ID,
        "workflow": "code_assist",
        "input": {"task": "Explain Python decorators"},
        "tools": ["calculator"],
        "model": "llama-3.3-70b-versatile"
    }
    resp = requests.post(f"{BASE_URL}/v1/runs", json=payload2, headers=headers)
    result = resp.json() if resp.status_code == 201 else {}
    results.append(log_test("Create: Run with model param", "POST", "/v1/runs", resp.status_code, 201, result))
    
    # Test 3: Get run details
    print(f"\n{BLUE}[Test Group: Run Retrieval]{RESET}")
    if RUN_ID:
        resp = requests.get(f"{BASE_URL}/v1/runs/{RUN_ID}", headers=headers)
        result = resp.json() if resp.status_code == 200 else {}
        results.append(log_test("Get: Run details", "GET", f"/v1/runs/{RUN_ID}", resp.status_code, 200, result))
        if resp.status_code == 200:
            print(f"  → Status: {result.get('status')}, Latency: {result.get('latency_ms')}ms")
    
    # Test 4: Get run trace
    if RUN_ID:
        resp = requests.get(f"{BASE_URL}/v1/runs/{RUN_ID}/trace", headers=headers)
        result = resp.json() if resp.status_code == 200 else {}
        results.append(log_test("Get: Run trace", "GET", f"/v1/runs/{RUN_ID}/trace", resp.status_code, 200, {"event_count": len(result) if isinstance(result, list) else 0}))
        if resp.status_code == 200:
            print(f"  → Trace events: {len(result) if isinstance(result, list) else 'N/A'}")
    
    # Test 5: Nonexistent run
    print(f"\n{BLUE}[Test Group: Error Handling]{RESET}")
    resp = requests.get(f"{BASE_URL}/v1/runs/nonexistent_run", headers=headers)
    results.append(log_test("Get: Nonexistent run", "GET", "/v1/runs/{id}", resp.status_code, 404))
    
    # Test 6: Invalid project
    bad_run = {
        "project_id": "invalid_project_id",
        "workflow": "code_assist",
        "input": {"task": "test"},
        "tools": []
    }
    resp = requests.post(f"{BASE_URL}/v1/runs", json=bad_run, headers=headers)
    # May fail at workflow level, but test the endpoint
    print(f"  → Run with invalid project: {resp.status_code}")
    
    return all(results)


# ============================================================================
# RETRIEVAL TESTS
# ============================================================================

def test_retrieval_detailed():
    """Detailed retrieval endpoint testing"""
    global TOKEN, PROJECT_ID
    if not TOKEN or not PROJECT_ID:
        print(f"{RED}Skipping retrieval (missing token/project){RESET}")
        return False
    
    section("RETRIEVAL ENDPOINTS - Detailed Tests")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    results = []
    
    # Test 1: Index document
    print(f"\n{BLUE}[Test Group: Document Indexing]{RESET}")
    payload = {
        "project_id": PROJECT_ID,
        "title": "Python Best Practices",
        "content": "Use meaningful variable names. Follow PEP 8. Write unit tests.",
        "source": "documentation"
    }
    resp = requests.post(f"{BASE_URL}/v1/retrieval/documents", json=payload, headers=headers)
    result = resp.json() if resp.status_code == 201 else {}
    results.append(log_test("Index: Single document", "POST", "/v1/retrieval/documents", resp.status_code, 201, result))
    
    # Test 2: Index multiple documents
    print(f"\n{BLUE}[Test Group: Batch Indexing]{RESET}")
    docs = [
        {"title": "FastAPI Guide", "content": "FastAPI is a modern web framework for Python."},
        {"title": "SQLAlchemy Basics", "content": "SQLAlchemy provides an ORM for database operations."}
    ]
    for i, doc in enumerate(docs):
        doc["project_id"] = PROJECT_ID
        doc["source"] = "guide"
        resp = requests.post(f"{BASE_URL}/v1/retrieval/documents", json=doc, headers=headers)
        results.append(log_test(f"Index: Document {i+2}", "POST", "/v1/retrieval/documents", resp.status_code, 201))
    
    # Test 3: Query documents
    print(f"\n{BLUE}[Test Group: Semantic Search]{RESET}")
    query_payload = {
        "project_id": PROJECT_ID,
        "query": "Python programming best practices",
        "top_k": 5
    }
    resp = requests.post(f"{BASE_URL}/v1/retrieval/query", json=query_payload, headers=headers)
    result = resp.json() if resp.status_code == 200 else {}
    results.append(log_test("Query: Semantic search", "POST", "/v1/retrieval/query", resp.status_code, 200, result))
    if resp.status_code == 200:
        results_list = result.get('results', [])
        print(f"  → Found {len(results_list)} results")
        for r in results_list[:2]:
            print(f"     - {r.get('title', 'N/A')} (score: {r.get('score', 'N/A')})")
    
    # Test 4: Query with different top_k
    query_payload["top_k"] = 2
    resp = requests.post(f"{BASE_URL}/v1/retrieval/query", json=query_payload, headers=headers)
    result = resp.json() if resp.status_code == 200 else {}
    results.append(log_test("Query: Limited results", "POST", "/v1/retrieval/query", resp.status_code, 200))
    
    # Test 5: Query empty results
    print(f"\n{BLUE}[Test Group: Edge Cases]{RESET}")
    query_payload["query"] = "xyzabc nonexistent query with random words"
    resp = requests.post(f"{BASE_URL}/v1/retrieval/query", json=query_payload, headers=headers)
    result = resp.json() if resp.status_code == 200 else {}
    results.append(log_test("Query: No matching results", "POST", "/v1/retrieval/query", resp.status_code, 200))
    
    # Test 6: Without auth
    resp = requests.post(f"{BASE_URL}/v1/retrieval/query", json=query_payload)
    results.append(log_test("Query: Without auth", "POST", "/v1/retrieval/query", resp.status_code, 401))
    
    return all(results)


# ============================================================================
# EVALUATION TESTS
# ============================================================================

def test_evaluate_detailed():
    """Detailed evaluation endpoint testing"""
    global TOKEN, PROJECT_ID, RUN_ID
    if not TOKEN or not PROJECT_ID or not RUN_ID:
        print(f"{RED}Skipping evaluation (missing token/project/run){RESET}")
        return False
    
    section("EVALUATION ENDPOINTS - Detailed Tests")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    results = []
    
    # Test 1: Evaluate completed run
    print(f"\n{BLUE}[Test Group: Run Evaluation]{RESET}")
    payload = {
        "run_id": RUN_ID,
        "criteria": ["correctness", "relevance", "safety"]
    }
    resp = requests.post(f"{BASE_URL}/v1/evaluate", json=payload, headers=headers)
    result = resp.json() if resp.status_code == 200 else {}
    results.append(log_test("Evaluate: Completed run", "POST", "/v1/evaluate", resp.status_code, 200, result))
    if resp.status_code == 200:
        scores = result.get('scores', {})
        print(f"  → Scores: {scores}")
        print(f"  → Rationale: {result.get('rationale', 'N/A')[:100]}...")
    
    # Test 2: Evaluate with custom criteria
    print(f"\n{BLUE}[Test Group: Custom Criteria]{RESET}")
    payload["criteria"] = ["accuracy", "efficiency"]
    resp = requests.post(f"{BASE_URL}/v1/evaluate", json=payload, headers=headers)
    result = resp.json() if resp.status_code == 200 else {}
    results.append(log_test("Evaluate: Custom criteria", "POST", "/v1/evaluate", resp.status_code, 200, result))
    
    # Test 3: Nonexistent run
    print(f"\n{BLUE}[Test Group: Error Handling]{RESET}")
    bad_payload = {
        "run_id": "nonexistent_run",
        "criteria": ["test"]
    }
    resp = requests.post(f"{BASE_URL}/v1/evaluate", json=bad_payload, headers=headers)
    results.append(log_test("Evaluate: Nonexistent run", "POST", "/v1/evaluate", resp.status_code, 404))
    
    # Test 4: Without auth
    resp = requests.post(f"{BASE_URL}/v1/evaluate", json=payload)
    results.append(log_test("Evaluate: Without auth", "POST", "/v1/evaluate", resp.status_code, 401))
    
    return all(results)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all detailed tests"""
    print(f"\n{CYAN}╔{'='*68}╗")
    print(f"║ {'AI Developer Toolkit - DETAILED Endpoint Testing':^66} ║")
    print(f"║ {'Testing: Edge Cases, Errors, Validation':^66} ║")
    print(f"║ {'API: ' + BASE_URL:^66} ║")
    print(f"╚{'='*68}╝{RESET}\n")
    
    test_groups = {
        "Auth": test_auth_detailed,
        "Projects": test_projects_detailed,
        "Prompts": test_prompts_detailed,
        "Tools": test_tools_detailed,
        "Runs": test_runs_detailed,
        "Retrieval": test_retrieval_detailed,
        "Evaluation": test_evaluate_detailed,
    }
    
    results = {}
    for name, test_func in test_groups.items():
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n{RED}Test group {name} crashed: {e}{RESET}")
            results[name] = False
    
    # Summary
    section("DETAILED TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, status in results.items():
        symbol = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
        print(f"{symbol} {test_name:20} {'PASS' if status else 'FAIL'}")
    
    print(f"\n{CYAN}Total: {passed}/{total} test groups passed{RESET}\n")
    
    if passed == total:
        print(f"{GREEN}All detailed tests passed! 🎉{RESET}\n")
    else:
        print(f"{YELLOW}Some tests need review. Check output above.{RESET}\n")


if __name__ == "__main__":
    main()
