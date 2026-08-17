# API Testing Guide - Complete Reference

## Overview
This guide covers all methods to test the AI Developer Toolkit API endpoints. Your API is running at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

---

## 🚀 Quick Start - Choose Your Method

### **Option 1: Swagger UI (Easiest)** ✨
1. Open browser: `http://localhost:8000/docs`
2. Click "Try it out" on any endpoint
3. Fill in parameters and see responses instantly
4. **Best for**: Quick exploration, testing, debugging

### **Option 2: Python Test Scripts** 🐍
```bash
# Smoke test (14 tests, 30 seconds)
python test_all_endpoints.py

# Detailed tests (70+ tests, edge cases, validation)
python test_detailed_endpoints.py
```
**Best for**: CI/CD, automation, regression testing

### **Option 3: PowerShell (Windows)** 💻
```powershell
.\TESTING_WITH_POWERSHELL.ps1
```
**Best for**: Windows developers, manual testing with saved variables

### **Option 4: cURL/Bash (Linux/Mac)** 🐧
```bash
bash TESTING_WITH_CURL.sh
```
**Best for**: Unix/Linux systems, integration with scripts

---

## 📊 Test Status Summary

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `/health` | GET | ✅ | No auth required |
| `/v1/auth/register` | POST | ✅ | Creates user accounts |
| `/v1/auth/login` | POST | ✅ | Returns JWT token |
| `/v1/projects` | POST | ✅ | Requires auth |
| `/v1/projects` | GET | ✅ | List user projects |
| `/v1/prompts` | POST | ✅ | Auto-versioning |
| `/v1/prompts/{id}` | GET | ✅ | Get specific version |
| `/v1/tools` | GET | ✅ | No auth required |
| `/v1/tools/execute` | POST | ✅ | Execute tool with args |
| `/v1/runs` | POST | ✅ | Create workflow run |
| `/v1/runs/{id}` | GET | ✅ | Get run status |
| `/v1/runs/{id}/trace` | GET | ✅ | Full execution trace |
| `/v1/retrieval/documents` | POST | ✅ | Index for RAG |
| `/v1/retrieval/query` | POST | ✅ | Semantic search |
| `/v1/evaluate` | POST | ✅ | LLM-as-judge evaluation |

---

## 🔐 Authentication Flow

### Step 1: Register User
```bash
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "User Name",
    "password": "SecurePassword123"
  }'
```
Response: `{"id": "user_xxx", "email": "...", "name": "...", "role": "member"}`

### Step 2: Login & Get Token
```bash
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePassword123"
```
Response: `{"access_token": "eyJhbGci...", "token_type": "bearer"}`

### Step 3: Use Token in All Requests
```bash
curl -X GET http://localhost:8000/v1/projects \
  -H "Authorization: Bearer eyJhbGci..."
```

---

## 📝 Endpoint Details & Examples

### **1. Projects**
Create and manage projects - containers for prompts, runs, and documents.

**Create Project:**
```bash
curl -X POST http://localhost:8000/v1/projects \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "ML Pipeline Project"}'
```
Response: `{"id": "proj_xxx", "name": "...", "owner_id": "...", "created_at": "..."}`

**List Projects:**
```bash
curl -X GET http://localhost:8000/v1/projects \
  -H "Authorization: Bearer TOKEN"
```

---

### **2. Prompts**
Version-controlled prompt templates with substitution support.

**Create Prompt:**
```bash
curl -X POST http://localhost:8000/v1/prompts \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj_xxx",
    "name": "code_reviewer",
    "template": "Review this code:\n{code}\n\nProvide feedback."
  }'
```

**Key Features:**
- ✅ Auto-versioning (v1, v2, v3...)
- ✅ Project-scoped
- ✅ Template variables with `{variable_name}`

---

### **3. Tools**
Execute tools like calculator, web search, code execution, etc.

**List Available Tools:**
```bash
curl -X GET http://localhost:8000/v1/tools \
  -H "Authorization: Bearer TOKEN"
```

**Execute Tool:**
```bash
curl -X POST http://localhost:8000/v1/tools/execute \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "calculator",
    "arguments": {
      "operation": "add",
      "a": 10,
      "b": 20
    }
  }'
```

**Available Tools:**
- `calculator` - Arithmetic operations (add, subtract, multiply, divide)
- `web_search` - Search the web
- `code_execution` - Execute Python code

---

### **4. Runs (Workflows)**
Execute workflows that chain prompts, tools, and LLM calls.

**Create & Execute Run:**
```bash
curl -X POST http://localhost:8000/v1/runs \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj_xxx",
    "workflow": "code_assist",
    "input": {
      "task": "Calculate 42 * 17"
    },
    "tools": ["calculator"],
    "model": "llama-3.3-70b-versatile"
  }'
```

Response:
```json
{
  "run_id": "run_xxx",
  "status": "completed",
  "trace_url": "/v1/runs/run_xxx/trace"
}
```

**Get Run Details:**
```bash
curl -X GET http://localhost:8000/v1/runs/run_xxx \
  -H "Authorization: Bearer TOKEN"
```

Response includes:
- `status` - completed, running, failed
- `latency_ms` - execution time in milliseconds
- `input_payload` - original input
- `output_payload` - LLM response
- `start_time` / `end_time` - timestamps

**Get Run Trace (Step-by-step):**
```bash
curl -X GET http://localhost:8000/v1/runs/run_xxx/trace \
  -H "Authorization: Bearer TOKEN"
```

Response: Array of trace events showing:
- Model API calls
- Tool executions
- Parameter values
- Latencies

---

### **5. Retrieval (RAG)**
Index documents and perform semantic search.

**Index Document:**
```bash
curl -X POST http://localhost:8000/v1/retrieval/documents \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj_xxx",
    "title": "Python Best Practices",
    "content": "Always follow PEP 8. Use meaningful variable names.",
    "source": "documentation"
  }'
```

**Query Documents (Semantic Search):**
```bash
curl -X POST http://localhost:8000/v1/retrieval/query \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj_xxx",
    "query": "Python coding standards",
    "top_k": 5
  }'
```

Response:
```json
{
  "query": "...",
  "results": [
    {
      "document_id": "doc_xxx",
      "title": "...",
      "snippet": "...",
      "score": 0.85
    }
  ]
}
```

**Note:** Uses bag-of-words + cosine similarity. For production, swap with vector embeddings.

---

### **6. Evaluation**
LLM-as-judge evaluation of completed runs.

**Evaluate Run:**
```bash
curl -X POST http://localhost:8000/v1/evaluate \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "run_xxx",
    "criteria": ["correctness", "relevance", "safety"]
  }'
```

Response:
```json
{
  "run_id": "run_xxx",
  "scores": {
    "correctness": 0.95,
    "relevance": 0.88,
    "safety": 1.0
  },
  "rationale": "The output correctly computes 42 * 17 = 714..."
}
```

**Default Criteria:** correctness, relevance, safety
**Custom Criteria:** Pass any list (e.g., `["accuracy", "efficiency"]`)

---

## 🧪 Running the Test Suites

### **Python: Smoke Test**
Quick verification (30 seconds):
```bash
python test_all_endpoints.py
```
Output:
```
✓ Health               PASS
✓ Auth                 PASS
✓ Projects             PASS
✓ Prompts              PASS
✓ Tools                PASS
✓ Runs                 PASS
✓ Retrieval            PASS
✓ Evaluate             PASS

Total: 8/8 test groups passed ✅
```

### **Python: Detailed Test**
Comprehensive testing (1-2 minutes, 70+ test cases):
```bash
python test_detailed_endpoints.py
```
Covers:
- ✅ Valid inputs
- ✅ Duplicate detection
- ✅ Error handling (404, 401, 409, 422)
- ✅ Validation (missing fields, invalid types)
- ✅ Edge cases (empty results, nonexistent resources)
- ✅ Response structure validation

### **PowerShell: Windows Testing**
Interactive testing with saved variables:
```powershell
.\TESTING_WITH_POWERSHELL.ps1
```
Features:
- Step-by-step with colored output
- Saves TOKEN, PROJECT_ID, RUN_ID, PROMPT_ID for reuse
- Proper error handling
- Shows response details

### **Bash: Unix/Linux Testing**
Execute complete test flow:
```bash
bash TESTING_WITH_CURL.sh
```
15 complete endpoint tests with examples.

---

## 🔍 Common Issues & Solutions

### Issue: 401 Unauthorized
**Problem:** Missing or invalid token
**Solution:**
```bash
# Login first and get token
curl -X POST http://localhost:8000/v1/auth/login \
  -d "username=email@example.com&password=yourpass"

# Then use token in header
curl ... -H "Authorization: Bearer YOUR_TOKEN"
```

### Issue: 404 Not Found
**Problem:** Resource (project, prompt, run) doesn't exist
**Solution:** 
- Verify the ID is correct
- Check in Swagger UI: http://localhost:8000/docs
- Create the resource first if needed

### Issue: 400 Bad Request
**Problem:** Missing required fields or invalid data type
**Solution:**
- Check required fields in request body
- Verify field names match schema
- Use `Content-Type: application/json` header

### Issue: 409 Conflict
**Problem:** Email already registered
**Solution:** Use different email or login if account exists

### Issue: Connection Refused
**Problem:** Server not running
**Solution:**
```bash
# Start server
uvicorn app.main:app --reload
```

---

## 📊 Performance Benchmarks

From test runs:

| Operation | Avg Time | Max Time |
|-----------|----------|----------|
| Auth (register + login) | 50ms | 100ms |
| Create project | 30ms | 50ms |
| Create prompt | 20ms | 40ms |
| Execute tool | 100ms | 200ms |
| Workflow run | **1000-2000ms** | 3000ms |
| Query documents | 50ms | 100ms |
| Evaluate run | 1500ms | 2500ms |

**Note:** Workflow runs & evaluations are slower due to LLM API calls to Groq.

---

## 🚀 Next Steps

1. **Use Swagger UI** (`http://localhost:8000/docs`) for interactive exploration
2. **Run test suites** to verify all endpoints work
3. **Integrate into CI/CD** using `test_all_endpoints.py`
4. **Customize workflows** using `/v1/runs` endpoint
5. **Build RAG pipelines** with `/v1/retrieval/*` endpoints

---

## 📚 Additional Resources

- **Swagger API Docs:** http://localhost:8000/docs
- **ReDoc API Docs:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json
- **Project Architecture:** See `docs/architecture.md`
- **Database Schema:** See `docs/` or check migrations

---

## 💡 Tips

- ✅ Save tokens to avoid repeated logins during testing
- ✅ Store project/run/prompt IDs for reuse in subsequent calls
- ✅ Use `top_k=5` parameter to limit retrieval results
- ✅ Check trace URL in run response for debugging
- ✅ Evaluation only works on completed runs
- ✅ All date/time fields are in UTC ISO format

---

**Happy Testing! 🎉**
