#!/bin/bash
# API Testing Guide - cURL Commands
# AI Developer Toolkit API
# Base URL: http://localhost:8000

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "AI Developer Toolkit - cURL Testing Guide"
echo "=========================================="

# ============================================================
# 1. HEALTH CHECK
# ============================================================
echo ""
echo "1. HEALTH CHECK"
echo "---"
curl -X GET $BASE_URL/health


# ============================================================
# 2. AUTH - REGISTER
# ============================================================
echo ""
echo ""
echo "2. AUTH - REGISTER"
echo "---"
curl -X POST $BASE_URL/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "name": "Test User",
    "password": "SecurePass123!"
  }'


# ============================================================
# 3. AUTH - LOGIN
# ============================================================
echo ""
echo ""
echo "3. AUTH - LOGIN"
echo "---"
echo "Run this and copy the access_token for Bearer auth:"
curl -X POST $BASE_URL/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser@example.com&password=SecurePass123!"


# ============================================================
# 4. CREATE PROJECT (requires Bearer token)
# ============================================================
echo ""
echo ""
echo "4. CREATE PROJECT"
echo "---"
echo "Replace TOKEN with the access_token from login above"
TOKEN="your_token_here"
curl -X POST $BASE_URL/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Project"
  }'


# ============================================================
# 5. LIST PROJECTS
# ============================================================
echo ""
echo ""
echo "5. LIST PROJECTS"
echo "---"
curl -X GET $BASE_URL/v1/projects \
  -H "Authorization: Bearer $TOKEN"


# ============================================================
# 6. CREATE PROMPT
# ============================================================
echo ""
echo ""
echo "6. CREATE PROMPT"
echo "---"
echo "Replace PROJECT_ID with ID from create project"
PROJECT_ID="proj_xxx"
curl -X POST $BASE_URL/v1/prompts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "'$PROJECT_ID'",
    "name": "code_reviewer",
    "template": "Review the following code:\n{code}\n\nProvide constructive feedback."
  }'


# ============================================================
# 7. GET PROMPT
# ============================================================
echo ""
echo ""
echo "7. GET PROMPT"
echo "---"
echo "Replace PROMPT_ID with ID from create prompt"
PROMPT_ID="prompt_xxx"
curl -X GET $BASE_URL/v1/prompts/$PROMPT_ID \
  -H "Authorization: Bearer $TOKEN"


# ============================================================
# 8. LIST TOOLS
# ============================================================
echo ""
echo ""
echo "8. LIST TOOLS"
echo "---"
curl -X GET $BASE_URL/v1/tools \
  -H "Authorization: Bearer $TOKEN"


# ============================================================
# 9. EXECUTE TOOL
# ============================================================
echo ""
echo ""
echo "9. EXECUTE TOOL - Calculator"
echo "---"
curl -X POST $BASE_URL/v1/tools/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "calculator",
    "arguments": {
      "operation": "add",
      "a": 10,
      "b": 20
    }
  }'


# ============================================================
# 10. CREATE RUN (Workflow Execution)
# ============================================================
echo ""
echo ""
echo "10. CREATE RUN - Workflow Execution"
echo "---"
curl -X POST $BASE_URL/v1/runs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "'$PROJECT_ID'",
    "workflow": "code_assist",
    "input": {
      "task": "Calculate 42 * 17 using the calculator"
    },
    "tools": ["calculator"],
    "model": "llama-3.3-70b-versatile"
  }'


# ============================================================
# 11. GET RUN DETAILS
# ============================================================
echo ""
echo ""
echo "11. GET RUN DETAILS"
echo "---"
echo "Replace RUN_ID with ID from create run"
RUN_ID="run_xxx"
curl -X GET $BASE_URL/v1/runs/$RUN_ID \
  -H "Authorization: Bearer $TOKEN"


# ============================================================
# 12. GET RUN TRACE
# ============================================================
echo ""
echo ""
echo "12. GET RUN TRACE (Step-by-step execution)"
echo "---"
curl -X GET $BASE_URL/v1/runs/$RUN_ID/trace \
  -H "Authorization: Bearer $TOKEN"


# ============================================================
# 13. INDEX DOCUMENT (Retrieval)
# ============================================================
echo ""
echo ""
echo "13. INDEX DOCUMENT - Add to RAG"
echo "---"
curl -X POST $BASE_URL/v1/retrieval/documents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "'$PROJECT_ID'",
    "title": "Python Best Practices",
    "content": "Always follow PEP 8. Use meaningful variable names. Write comprehensive tests. Document your code.",
    "source": "documentation"
  }'


# ============================================================
# 14. QUERY DOCUMENTS (Semantic Search)
# ============================================================
echo ""
echo ""
echo "14. QUERY DOCUMENTS - Semantic Search"
echo "---"
curl -X POST $BASE_URL/v1/retrieval/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "'$PROJECT_ID'",
    "query": "Python coding standards",
    "top_k": 5
  }'


# ============================================================
# 15. EVALUATE RUN
# ============================================================
echo ""
echo ""
echo "15. EVALUATE RUN - LLM-as-Judge"
echo "---"
curl -X POST $BASE_URL/v1/evaluate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "'$RUN_ID'",
    "criteria": ["correctness", "relevance", "safety"]
  }'


echo ""
echo ""
echo "=========================================="
echo "Testing Complete!"
echo "=========================================="
