# Unified Memory System - Windows PowerShell Launcher
# Автоматический запуск с диагностикой и проверками

param(
    [switch]$Clean,          # Очистить старые данные
    [switch]$Monitoring,     # Запустить с мониторингом
    [switch]$Minimal,        # Минимальная конфигурация
    [switch]$DevMode,        # Режим разработки
    [switch]$ForceRebuild,   # Принудительная пересборка без кэша
    [switch]$Help            # Показать справку
)

# Цвета для вывода
$ErrorColor = "Red"
$SuccessColor = "Green"
$WarningColor = "Yellow"
$InfoColor = "Cyan"

function Write-Status {
    param([string]$Message, [string]$Status = "INFO")
    
    switch ($Status) {
        "SUCCESS" { Write-Host "✅ $Message" -ForegroundColor $SuccessColor }
        "ERROR"   { Write-Host "❌ $Message" -ForegroundColor $ErrorColor }
        "WARNING" { Write-Host "⚠️ $Message" -ForegroundColor $WarningColor }
        "INFO"    { Write-Host "ℹ️ $Message" -ForegroundColor $InfoColor }
        default   { Write-Host $Message }
    }
}

function Show-Help {
    Write-Host @"

🚀 UNIFIED MEMORY SYSTEM - WINDOWS LAUNCHER

ИСПОЛЬЗОВАНИЕ:
  .\запуск_windows.ps1 [параметры]

ПАРАМЕТРЫ:
  -Clean          Очистить старые данные Docker перед запуском
  -Monitoring     Запустить с Prometheus + Grafana мониторингом
  -Minimal        Запустить только Neo4j + Memory Server (быстрее)
  -DevMode        Режим разработки с живыми логами
  -ForceRebuild   ПРИНУДИТЕЛЬНАЯ пересборка без кэша (исправляет embedding_dims)
  -Help           Показать эту справку

ПРИМЕРЫ:
  .\запуск_windows.ps1                    # Обычный запуск
  .\запуск_windows.ps1 -Clean             # Запуск с очисткой
  .\запуск_windows.ps1 -Monitoring        # Запуск с мониторингом
  .\запуск_windows.ps1 -Minimal           # Минимальная конфигурация
  .\запуск_windows.ps1 -DevMode           # Разработческий режим
  .\запуск_windows.ps1 -ForceRebuild      # Исправление ошибки embedding_dims

"@ -ForegroundColor $InfoColor
    exit
}

if ($Help) { Show-Help }

Write-Host @"

==========================================
🚀 UNIFIED MEMORY SYSTEM - LAUNCHER
==========================================

"@ -ForegroundColor $InfoColor

# Проверка Docker
Write-Status "Проверяем Docker..." "INFO"
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -ne 0) { throw "Docker не найден" }
    Write-Status "Docker найден: $dockerVersion" "SUCCESS"
} catch {
    Write-Status "Docker не найден! Установите Docker Desktop" "ERROR"
    exit 1
}

# Проверка Docker Compose
Write-Status "Проверяем Docker Compose..." "INFO"
try {
    $composeVersion = docker-compose --version 2>$null
    if ($LASTEXITCODE -ne 0) { throw "Docker Compose не найден" }
    Write-Status "Docker Compose найден: $composeVersion" "SUCCESS"
} catch {
    Write-Status "Docker Compose не найден!" "ERROR"
    exit 1
}

# Проверка .env файла
Write-Status "Проверяем конфигурацию..." "INFO"
if (-not (Test-Path ".env")) {
    Write-Status "Файл .env не найден. Создаем из config.example.env..." "WARNING"
    Copy-Item "config.example.env" ".env"
    Write-Status "Создан файл .env" "SUCCESS"
    Write-Host @"

📝 ВАЖНО: Настройте файл .env!
   Откройте .env в текстовом редакторе и укажите:
   - OPENAI_API_KEY=your_actual_api_key

"@ -ForegroundColor $WarningColor
    
    $response = Read-Host "Открыть .env в блокноте? (Y/n)"
    if ($response -ne "n" -and $response -ne "N") {
        notepad ".env"
        Read-Host "Нажмите Enter после настройки .env"
    }
}

# Проверка API ключа в .env
$envContent = Get-Content ".env" -ErrorAction SilentlyContinue
$apiKeyLine = $envContent | Where-Object { $_ -like "OPENAI_API_KEY=*" }
if ($apiKeyLine -like "*your_openai_api_key_here*" -or $apiKeyLine -like "*=*" -and $apiKeyLine.Split("=")[1].Length -lt 10) {
    Write-Status "⚠️ Похоже, OPENAI_API_KEY не настроен в .env файле!" "WARNING"
    $response = Read-Host "Продолжить? Система может не работать без API ключа (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        exit 1
    }
}

Write-Status "Конфигурация проверена" "SUCCESS"

# Остановка старых контейнеров
Write-Status "Останавливаем старые контейнеры..." "INFO"
docker-compose -f docker-compose.unified.yml down 2>$null
Write-Status "Старые контейнеры остановлены" "SUCCESS"

# Очистка (если запрошена)
if ($Clean) {
    Write-Status "Очищаем старые данные Docker..." "INFO"
    docker system prune -f 2>$null
    docker volume prune -f 2>$null
    Write-Status "Очистка завершена" "SUCCESS"
}

# Принудительная пересборка (для исправления embedding_dims)
if ($ForceRebuild) {
    Write-Status "ПРИНУДИТЕЛЬНАЯ ПЕРЕСБОРКА без кэша..." "WARNING"
    Write-Status "Это исправит ошибку embedding_dims" "INFO"
    
    # Полная очистка Docker
    docker stop $(docker ps -aq) 2>$null
    docker rm $(docker ps -aq) 2>$null
    docker rmi $(docker images -q) -f 2>$null
    docker volume rm $(docker volume ls -q) 2>$null
    docker builder prune -af
    
    Write-Status "Все Docker данные очищены" "SUCCESS"
    Write-Status "Начинаем пересборку без кэша..." "INFO"
}

# Определение команды запуска
$composeCommand = "docker-compose -f docker-compose.unified.yml"

$buildArgs = if ($ForceRebuild) { " --build --no-cache" } else { " --build" }

if ($Monitoring) {
    Write-Status "Запуск с мониторингом (Prometheus + Grafana)..." "INFO"
    $composeCommand += " --profile monitoring up -d$buildArgs"
} elseif ($Minimal) {
    Write-Status "Запуск минимальной конфигурации..." "INFO"
    $composeCommand += " up -d neo4j postgres memory-server$buildArgs"
} elseif ($DevMode) {
    Write-Status "Запуск в режиме разработки..." "INFO"
    $composeCommand += " up$buildArgs"
} else {
    Write-Status "Запуск стандартной конфигурации..." "INFO"
    $composeCommand += " up -d$buildArgs"
}

if ($ForceRebuild) {
    Write-Host "`n⚠️ ПРИНУДИТЕЛЬНАЯ ПЕРЕСБОРКА: Это займет 5-10 минут, но исправит ошибку embedding_dims`n" -ForegroundColor $WarningColor
} else {
    Write-Host "`nЭто может занять несколько минут при первом запуске...`n" -ForegroundColor $WarningColor
}

# Запуск системы
try {
    Invoke-Expression $composeCommand
    if ($LASTEXITCODE -ne 0) { throw "Ошибка запуска Docker Compose" }
    Write-Status "Система запускается..." "SUCCESS"
} catch {
    Write-Status "Ошибка запуска! Проверьте логи: docker-compose -f docker-compose.unified.yml logs" "ERROR"
    exit 1
}

if (-not $DevMode) {
    # Ожидание запуска
    Write-Status "Ожидаем запуска сервисов (30 сек)..." "INFO"
    Start-Sleep -Seconds 30

    # Проверка состояния контейнеров
    Write-Status "Проверяем состояние контейнеров..." "INFO"
    docker-compose -f docker-compose.unified.yml ps

    # Проверка здоровья API
    Write-Status "Проверяем Memory Server..." "INFO"
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8051/health" -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
        Write-Status "Memory Server работает!" "SUCCESS"
    } catch {
        Write-Status "Memory Server еще не готов, ожидаем еще 10 секунд..." "WARNING"
        Start-Sleep -Seconds 10
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8051/health" -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
            Write-Status "Memory Server работает!" "SUCCESS"
        } catch {
            Write-Status "Memory Server не отвечает. Проверьте логи: docker-compose -f docker-compose.unified.yml logs memory-server" "ERROR"
        }
    }

    # Финальная информация
    Write-Host @"

==========================================
🎉 СИСТЕМА ЗАПУЩЕНА!
==========================================

📊 Доступные интерфейсы:
"@ -ForegroundColor $SuccessColor

    Write-Host "   • Memory API:     " -NoNewline; Write-Host "http://localhost:8051/docs" -ForegroundColor $InfoColor
    Write-Host "   • Health Check:   " -NoNewline; Write-Host "http://localhost:8051/health" -ForegroundColor $InfoColor
    Write-Host "   • Neo4j Browser:  " -NoNewline; Write-Host "http://localhost:7474" -ForegroundColor $InfoColor
    
    if ($Monitoring) {
        Write-Host "   • Grafana:        " -NoNewline; Write-Host "http://localhost:3000" -ForegroundColor $InfoColor
        Write-Host "   • Prometheus:     " -NoNewline; Write-Host "http://localhost:9090" -ForegroundColor $InfoColor
    }

    Write-Host @"

🧪 Тестовые команды:
   • curl -X POST http://localhost:8051/memory/save -H "Content-Type: application/json" -d '{"content":"Тест Windows","user_id":"test"}'
   • curl -X POST http://localhost:8051/memory/search -H "Content-Type: application/json" -d '{"query":"Windows","user_id":"test"}'

🛑 Управление системой:
   • Остановка: docker-compose -f docker-compose.unified.yml down
   • Логи:      docker-compose -f docker-compose.unified.yml logs -f memory-server
   • Статус:    docker-compose -f docker-compose.unified.yml ps

"@ -ForegroundColor $InfoColor

    # Предложение открыть браузер
    $response = Read-Host "Открыть Memory API в браузере? (Y/n)"
    if ($response -ne "n" -and $response -ne "N") {
        Start-Process "http://localhost:8051/docs"
    }
} else {
    Write-Host @"

🔧 РЕЖИМ РАЗРАБОТКИ
Логи отображаются в реальном времени.
Нажмите Ctrl+C для остановки.

"@ -ForegroundColor $WarningColor
} 