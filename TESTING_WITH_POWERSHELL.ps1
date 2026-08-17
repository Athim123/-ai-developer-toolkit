# API Testing Guide - PowerShell (Windows)
# AI Developer Toolkit API
# Base URL: http://localhost:8000

$BASE_URL = "http://localhost:8000"
$TOKEN = ""
$PROJECT_ID = ""
$PROMPT_ID = ""
$RUN_ID = ""

Write-Host "==========================================`n" -ForegroundColor Cyan
Write-Host "AI Developer Toolkit - PowerShell Testing Guide" -ForegroundColor Cyan
Write-Host "===========================================`n" -ForegroundColor Cyan

# ============================================================
# 1. HEALTH CHECK
# ============================================================
Write-Host "1. HEALTH CHECK" -ForegroundColor Yellow
Write-Host "---" -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$BASE_URL/health" -Method Get
Write-Host ($response | ConvertTo-Json) -ForegroundColor Green


# ============================================================
# 2. AUTH - REGISTER
# ============================================================
Write-Host "`n2. AUTH - REGISTER" -ForegroundColor Yellow
Write-Host "---" -ForegroundColor Yellow
$registerBody = @{
    email = "testuser@example.com"
    name = "Test User"
    password = "SecurePass123!"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/v1/auth/register" `
        -Method Post `
        -Headers @{"Content-Type" = "application/json"} `
        -Body $registerBody
    Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}


# ============================================================
# 3. AUTH - LOGIN
# ============================================================
Write-Host "`n3. AUTH - LOGIN" -ForegroundColor Yellow
Write-Host "---" -ForegroundColor Yellow
Write-Host "Logging in..." -ForegroundColor Cyan

$loginBody = @{
    username = "testuser@example.com"
    password = "SecurePass123!"
}

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/v1/auth/login" `
        -Method Post `
        -Body $loginBody
    Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
    $TOKEN = $response.access_token
    Write-Host "Token saved for subsequent requests" -ForegroundColor Cyan
} catch {
    Write-Host "Login failed: $($_.Exception.Message)" -ForegroundColor Red
}


# ============================================================
# 4. CREATE PROJECT
# ============================================================
Write-Host "`n4. CREATE PROJECT" -ForegroundColor Yellow
Write-Host "---" -ForegroundColor Yellow

if ($TOKEN) {
    $projectBody = @{
        name = "My First Project"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/v1/projects" `
            -Method Post `
            -Headers @{
                "Authorization" = "Bearer $TOKEN"
                "Content-Type" = "application/json"
            } `
            -Body $projectBody
        Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
        $PROJECT_ID = $response.id
        Write-Host "Project ID saved: $PROJECT_ID" -ForegroundColor Cyan
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "No token available. Please login first." -ForegroundColor Red
}


# ============================================================
# 5. LIST PROJECTS
# ============================================================
Write-Host "`n5. LIST PROJECTS" -ForegroundColor Yellow
Write-Host "---" -ForegroundColor Yellow

if ($TOKEN) {
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/v1/projects" `
            -Method Get `
            -Headers @{"Authorization" = "Bearer $TOKEN"}
        Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}


# ============================================================
# 6. CREATE PROMPT
# ============================================================
Write-Host "`n6. CREATE PROMPT" -ForegroundColor Yellow
Write-Host "---" -ForegroundColor Yellow

if ($TOKEN -and $PROJECT_ID) {
    $promptBody = @{
        project_id = $PROJECT_ID
        name = "code_reviewer"
        template = "Review the following code:`n{code}`n`nProvide constructive feedback."
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/v1/prompts" `
            -Method Post `
            -Headers @{
                "Authorization" = "Bearer $TOKEN"
                "Content-Type" = "application/json"
            } `
            -Body $promptBody
        Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
        $PROMPT_ID = $response.id
        Write-Host "Prompt ID saved: $PROMPT_ID" -ForegroundColor Cyan
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}


# ============================================================
# 7. GET PROMPT
# ============================================================
Write-Host "`n7. GET PROMPT" -ForegroundColor Yellow
Write-Host "---" -ForegroundColor Yellow

if ($TOKEN -and $PROMPT_ID) {
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/v1/prompts/$PROMPT_ID" `
            -Method Get `
            -Headers @{"Authorization" = "Bearer $TOKEN"}
        Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}


# ============================================================
# 8. LIST TOOLS
# ============================================================
Write-Host "`n8. LIST TOOLS" -ForegroundColor Yellow
Write-Host "---" -ForegroundColor Yellow

if ($TOKEN) {
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/v1/tools" `
            -Method Get `
            -Headers @{"Authorization" = "Bearer $TOKEN"}
        Write-Host ($response | ConvertTo-Json -Depth 3) -ForegroundColor Green
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}


# ============================================================
# 9. EXECUTE TOOL - Calculator
# ============================================================
Write-Host "`n9. EXECUTE TOOL - Calculator" -ForegroundColor Yellow
Write-Host "---" -ForegroundColor Yellow

if ($TOKEN) {
    $toolBody = @{
        tool_name = "calculator"
        arguments = @{
            operation = "add"
            a = 10
            b = 20
        }
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/v1/tools/execute" `
            -Method Post `
            -Headers @{
                "Authorization" = "Bearer $TOKEN"
                "Content-Type" = "application/json"
            } `
            -Body $toolBody
        Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}


# ============================================================
# 10. CREATE RUN (Workflow)
# ============================================================
Write-Host "`n10. CREATE RUN - Workflow Execution" -ForegroundColor Yellow
Write-Host "---" -ForegroundColor Yellow

if ($TOKEN -and $PROJECT_ID) {
    $runBody = @{
        project_id = $PROJECT_ID
        workflow = "code_assist"
        input = @{
            task = "Calculate 42 * 17 using the calculator"
        }
        tools = @("calculator")
        model = "llama-3.3-70b-versatile"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/v1/runs" `
            -Method Post `
            -Headers @{
                "Authorization" = "Bearer $TOKEN"
                "Content-Type" = "application/json"
            } `
            -Body $runBody
        Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
        $RUN_ID = $response.run_id
        Write-Host "Run ID saved: $RUN_ID" -ForegroundColor Cyan
        Write-Host "Trace URL: $($response.trace_url)" -ForegroundColor Cyan
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}


# ============================================================
# 11. GET RUN DETAILS
# ============================================================
Write-Host "`n11. GET RUN DETAILS" -ForegroundColor Yellow
Write-Host "---" -ForegroundColor Yellow

if ($TOKEN -and $RUN_ID) {
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/v1/runs/$RUN_ID" `
            -Method Get `
            -Headers @{"Authorization" = "Bearer $TOKEN"}
        Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
        Write-Host "Status: $($response.status)" -ForegroundColor Cyan
        Write-Host "Latency: $($response.latency_ms)ms" -ForegroundColor Cyan
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}


# ============================================================
# 12. GET RUN TRACE
# ============================================================
Write-Host "`n12. GET RUN TRACE (Step-by-step)" -ForegroundColor Yellow
Write-Host "---" -ForegroundColor Yellow

if ($TOKEN -and $RUN_ID) {
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/v1/runs/$RUN_ID/trace" `
            -Method Get `
            -Headers @{"Authorization" = "Bearer $TOKEN"}
        Write-Host ($response | ConvertTo-Json -Depth 2) -ForegroundColor Green
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}


# ============================================================
# 13. INDEX DOCUMENT
# ============================================================
Write-Host "`n13. INDEX DOCUMENT - Retrieval/RAG" -ForegroundColor Yellow
Write-Host "---" -ForegroundColor Yellow

if ($TOKEN -and $PROJECT_ID) {
    $docBody = @{
        project_id = $PROJECT_ID
        title = "Python Best Practices"
        content = "Always follow PEP 8. Use meaningful variable names. Write comprehensive tests."
        source = "documentation"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/v1/retrieval/documents" `
            -Method Post `
            -Headers @{
                "Authorization" = "Bearer $TOKEN"
                "Content-Type" = "application/json"
            } `
            -Body $docBody
        Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}


# ============================================================
# 14. QUERY DOCUMENTS
# ============================================================
Write-Host "`n14. QUERY DOCUMENTS - Semantic Search" -ForegroundColor Yellow
Write-Host "---" -ForegroundColor Yellow

if ($TOKEN -and $PROJECT_ID) {
    $queryBody = @{
        project_id = $PROJECT_ID
        query = "Python coding standards"
        top_k = 5
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/v1/retrieval/query" `
            -Method Post `
            -Headers @{
                "Authorization" = "Bearer $TOKEN"
                "Content-Type" = "application/json"
            } `
            -Body $queryBody
        Write-Host ($response | ConvertTo-Json -Depth 2) -ForegroundColor Green
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}


# ============================================================
# 15. EVALUATE RUN
# ============================================================
Write-Host "`n15. EVALUATE RUN - LLM-as-Judge" -ForegroundColor Yellow
Write-Host "---" -ForegroundColor Yellow

if ($TOKEN -and $RUN_ID) {
    $evalBody = @{
        run_id = $RUN_ID
        criteria = @("correctness", "relevance", "safety")
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/v1/evaluate" `
            -Method Post `
            -Headers @{
                "Authorization" = "Bearer $TOKEN"
                "Content-Type" = "application/json"
            } `
            -Body $evalBody
        Write-Host ($response | ConvertTo-Json) -ForegroundColor Green
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}


Write-Host "`n==========================================`n" -ForegroundColor Cyan
Write-Host "Testing Complete!" -ForegroundColor Green
Write-Host "===========================================`n" -ForegroundColor Cyan
