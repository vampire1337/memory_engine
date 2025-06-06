@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo 🚀 UNIFIED MEMORY SYSTEM - WINDOWS LAUNCHER
echo ==========================================
echo.

:: Проверка Docker
echo [1/6] Проверяем Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker не найден! Установите Docker Desktop
    pause
    exit /b 1
)
echo ✅ Docker найден

:: Проверка Docker Compose
echo.
echo [2/6] Проверяем Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose не найден!
    pause
    exit /b 1
)
echo ✅ Docker Compose найден

:: Проверка .env файла
echo.
echo [3/6] Проверяем конфигурацию...
if not exist .env (
    echo ⚠️ Файл .env не найден. Копируем из config.example.env...
    copy config.example.env .env >nul
    echo ✅ Создан файл .env. ОБЯЗАТЕЛЬНО укажите ваш OPENAI_API_KEY!
    echo.
    echo 📝 Откройте .env в блокноте и установите ваш API ключ OpenAI
    notepad .env
    echo.
    echo Нажмите любую клавишу после настройки .env...
    pause >nul
)
echo ✅ Конфигурация найдена

:: Остановка старых контейнеров
echo.
echo [4/6] Останавливаем старые контейнеры...
docker-compose -f docker-compose.unified.yml down >nul 2>&1
echo ✅ Старые контейнеры остановлены

:: Очистка старых данных (опционально)
echo.
set /p cleanup="Очистить старые данные Docker? (y/N): "
if /i "%cleanup%"=="y" (
    echo Очищаем старые данные...
    docker system prune -f >nul 2>&1
    echo ✅ Очистка завершена
)

:: Запуск системы
echo.
echo [5/6] Запускаем Unified Memory System...
echo Это может занять несколько минут при первом запуске...
echo.

docker-compose -f docker-compose.unified.yml up -d --build

if %errorlevel% neq 0 (
    echo ❌ Ошибка запуска! Проверьте логи:
    echo docker-compose -f docker-compose.unified.yml logs
    pause
    exit /b 1
)

:: Ожидание запуска
echo.
echo [6/6] Ожидаем запуска сервисов...
timeout /t 30 /nobreak >nul

:: Проверка здоровья
echo.
echo 🔍 Проверяем состояние сервисов...
docker-compose -f docker-compose.unified.yml ps

echo.
echo 🩺 Проверяем health API...
curl -s http://localhost:8051/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Memory Server работает!
) else (
    echo ⚠️ Memory Server еще не готов, ожидаем...
    timeout /t 10 /nobreak >nul
    curl -s http://localhost:8051/health >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Memory Server работает!
    ) else (
        echo ❌ Memory Server не отвечает. Проверьте логи:
        echo docker-compose -f docker-compose.unified.yml logs memory-server
    )
)

echo.
echo ==========================================
echo 🎉 СИСТЕМА ЗАПУЩЕНА!
echo ==========================================
echo.
echo 📊 Доступные интерфейсы:
echo   • Memory API: http://localhost:8051/docs
echo   • Health Check: http://localhost:8051/health  
echo   • Neo4j Browser: http://localhost:7474
echo   • Логи: docker-compose -f docker-compose.unified.yml logs -f memory-server
echo.
echo 🧪 Тестовые команды:
echo   • curl -X POST http://localhost:8051/memory/save -H "Content-Type: application/json" -d "{\"content\":\"Тест\",\"user_id\":\"test\"}"
echo   • curl -X POST http://localhost:8051/memory/search -H "Content-Type: application/json" -d "{\"query\":\"Тест\",\"user_id\":\"test\"}"
echo.
echo 🛑 Остановка системы:
echo   • docker-compose -f docker-compose.unified.yml down
echo.

set /p open_browser="Открыть Memory API в браузере? (Y/n): "
if /i not "%open_browser%"=="n" (
    start http://localhost:8051/docs
)

echo.
echo Нажмите любую клавишу для выхода...
pause >nul 