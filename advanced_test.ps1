# Продвинутое тестирование Unified Memory System
$baseUrl = "http://localhost:8051"

# Тест 6: Entity Relationships
Write-Host "=== TEST 6: Entity Relationships ===" -ForegroundColor Green
$entityBody = @{
    entity_name = "Heist1337"
    user_id = "heist1337"
} | ConvertTo-Json -Depth 2

try {
    $entityResponse = Invoke-RestMethod -Uri "$baseUrl/graph/entity-relationships" -Method POST -Body $entityBody -ContentType "application/json"
    Write-Host "Entity Response: $($entityResponse | ConvertTo-Json -Depth 5)" -ForegroundColor Yellow
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Тест 7: Verified Memory
Write-Host "`n=== TEST 7: Save Verified Memory ===" -ForegroundColor Green
$verifiedBody = @{
    content = "VERIFIED: Neo4j graph database provides 26% better performance for relationship queries compared to traditional SQL joins"
    confidence = 0.95
    source = "benchmark_study"
    user_id = "heist1337"
    metadata = @{
        category = "research"
        priority = "critical"
        tags = @("neo4j", "performance", "research")
    }
} | ConvertTo-Json -Depth 3

try {
    $verifiedResponse = Invoke-RestMethod -Uri "$baseUrl/memory/save-verified" -Method POST -Body $verifiedBody -ContentType "application/json"
    Write-Host "Verified Response: $($verifiedResponse | ConvertTo-Json)" -ForegroundColor Yellow
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Тест 8: Project Milestone
Write-Host "`n=== TEST 8: Save Project Milestone ===" -ForegroundColor Green
$milestoneBody = @{
    milestone_name = "Unified Memory System V1.0 Launch"
    description = "Successfully deployed enterprise-grade memory system with 15 tools, Docker containerization, and full Mem0 SDK integration"
    project_id = "unified-memory-system"
    user_id = "heist1337"
    metadata = @{
        category = "achievement"
        priority = "critical"
        tags = @("milestone", "production", "success")
    }
} | ConvertTo-Json -Depth 3

try {
    $milestoneResponse = Invoke-RestMethod -Uri "$baseUrl/memory/save-milestone" -Method POST -Body $milestoneBody -ContentType "application/json"
    Write-Host "Milestone Response: $($milestoneResponse | ConvertTo-Json)" -ForegroundColor Yellow
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Тест 9: Get Accurate Context
Write-Host "`n=== TEST 9: Get Accurate Context ===" -ForegroundColor Green
$contextBody = @{
    query = "Docker Neo4j performance unified system"
    user_id = "heist1337"
    limit = 3
} | ConvertTo-Json -Depth 2

try {
    $contextResponse = Invoke-RestMethod -Uri "$baseUrl/memory/get-context" -Method POST -Body $contextBody -ContentType "application/json"
    Write-Host "Context Response: $($contextResponse | ConvertTo-Json -Depth 5)" -ForegroundColor Yellow
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Тест 10: Graph Status
Write-Host "`n=== TEST 10: Graph Status ===" -ForegroundColor Green
try {
    $statusResponse = Invoke-RestMethod -Uri "$baseUrl/graph/status" -Method GET
    Write-Host "Graph Status: $($statusResponse | ConvertTo-Json -Depth 5)" -ForegroundColor Yellow
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Тест 11: Health Check
Write-Host "`n=== TEST 11: System Health ===" -ForegroundColor Green
try {
    $healthResponse = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "Health Status: $($healthResponse | ConvertTo-Json -Depth 5)" -ForegroundColor Yellow
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== ADVANCED TESTING COMPLETED ===" -ForegroundColor Green 