# Скрипт для тестирования Unified Memory System
$baseUrl = "http://localhost:8051"

# Тест 1: Сохранение технической памяти
Write-Host "=== TEST 1: Save Technical Memory ===" -ForegroundColor Green
$body1 = @{
    content = "Technical memory: Docker multi-stage builds reduce image size significantly"
    user_id = "heist1337"
    metadata = @{
        category = "technical"
        priority = "high"
        tags = @("docker", "optimization")
    }
} | ConvertTo-Json -Depth 3

try {
    $response1 = Invoke-RestMethod -Uri "$baseUrl/memory/save" -Method POST -Body $body1 -ContentType "application/json"
    Write-Host "Response: $($response1 | ConvertTo-Json)" -ForegroundColor Yellow
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Тест 2: Сохранение личной памяти  
Write-Host "`n=== TEST 2: Save Personal Memory ===" -ForegroundColor Green
$body2 = @{
    content = "Personal memory: I love coding with synthwave music like Carpenter Brut and Perturbator"
    user_id = "heist1337"
    metadata = @{
        category = "personal"
        priority = "medium"
        tags = @("music", "productivity", "synthwave")
    }
} | ConvertTo-Json -Depth 3

try {
    $response2 = Invoke-RestMethod -Uri "$baseUrl/memory/save" -Method POST -Body $body2 -ContentType "application/json"
    Write-Host "Response: $($response2 | ConvertTo-Json)" -ForegroundColor Yellow
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Тест 3: Поиск памяти
Write-Host "`n=== TEST 3: Search Memories ===" -ForegroundColor Green
$searchBody = @{
    query = "Docker optimization"
    user_id = "heist1337"
    limit = 5
} | ConvertTo-Json -Depth 2

try {
    $searchResponse = Invoke-RestMethod -Uri "$baseUrl/memory/search" -Method POST -Body $searchBody -ContentType "application/json"
    Write-Host "Search Results: $($searchResponse | ConvertTo-Json -Depth 5)" -ForegroundColor Yellow
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Тест 4: Graph Memory
Write-Host "`n=== TEST 4: Save Graph Memory ===" -ForegroundColor Green
$graphBody = @{
    content = "Project memory: Heist1337 leads the development team creating Unified Memory System with Neo4j graph database and PostgreSQL storage"
    user_id = "heist1337"
    metadata = @{
        category = "project"
        priority = "high"
        tags = @("leadership", "database", "architecture")
    }
} | ConvertTo-Json -Depth 3

try {
    $graphResponse = Invoke-RestMethod -Uri "$baseUrl/graph/save-memory" -Method POST -Body $graphBody -ContentType "application/json"
    Write-Host "Graph Response: $($graphResponse | ConvertTo-Json)" -ForegroundColor Yellow
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Тест 5: Получить все воспоминания
Write-Host "`n=== TEST 5: Get All Memories ===" -ForegroundColor Green
$getAllBody = @{
    user_id = "heist1337"
} | ConvertTo-Json -Depth 2

try {
    $allMemories = Invoke-RestMethod -Uri "$baseUrl/memory/get-all" -Method POST -Body $getAllBody -ContentType "application/json"
    Write-Host "All Memories Count: $($allMemories.memories.Count)" -ForegroundColor Yellow
    $allMemories.memories | ForEach-Object {
        Write-Host "- ID: $($_.id), Content: $($_.content.Substring(0, [Math]::Min(60, $_.content.Length)))..." -ForegroundColor Cyan
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== TESTING COMPLETED ===" -ForegroundColor Green 