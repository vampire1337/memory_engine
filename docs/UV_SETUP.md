# 🚀 UV Setup для MCP-Mem0

UV - это сверхбыстрый Python package installer и resolver, написанный на Rust.

## 📦 Установка UV

### Windows (PowerShell)
```powershell
# Установка через PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Или через Scoop
scoop install uv

# Или через Chocolatey  
choco install uv
```

### Linux/macOS
```bash
# Установка через curl
curl -LsSf https://astral.sh/uv/install.sh | sh

# Или через Homebrew (macOS)
brew install uv
```

## 🏗️ Настройка проекта

### 1. Инициализация проекта
```bash
# Переход в директорию проекта
cd mcp-mem0

# Создание виртуального окружения
uv venv

# Активация (Windows)
.\.venv\Scripts\activate

# Активация (Linux/macOS)
source .venv/bin/activate
```

### 2. Установка зависимостей
```bash
# Установка основных зависимостей
uv pip install -e .

# Установка dev зависимостей
uv pip install -e ".[dev]"

# Установка всех optional зависимостей
uv pip install -e ".[dev,monitoring,redis]"
```

### 3. Быстрая установка без активации venv
```bash
# UV автоматически создаст и использует venv
uv run python src/unified_memory_server.py

# Или запуск через entry point
uv run mcp-mem0

# Установка и запуск одной командой
uv run --with fastapi uvicorn src.unified_memory_server:app --host 0.0.0.0 --port 8051
```

## ⚡ Преимущества UV

| **Аспект** | **pip** | **UV** |
|------------|---------|--------|
| **Скорость установки** | 30-60 секунд | 2-5 секунд |
| **Разрешение зависимостей** | Медленное | Мгновенное |
| **Кэширование** | Базовое | Агрессивное |
| **Parallel downloads** | Ограниченно | Полная поддержка |
| **Lock файлы** | Нет | Есть |

## 🔧 Команды разработки

### Установка и запуск
```bash
# Быстрая установка всех зависимостей
uv sync

# Запуск сервера
uv run python src/unified_memory_server.py

# Запуск тестов
uv run pytest

# Форматирование кода
uv run black src/
uv run isort src/

# Линтинг
uv run ruff check src/
uv run mypy src/
```

### Docker интеграция
```dockerfile
# В Dockerfile можно использовать UV для быстрой установки
FROM python:3.11-slim

# Установка UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Копирование файлов проекта
COPY pyproject.toml uv.lock ./

# Быстрая установка зависимостей
RUN uv sync --frozen --no-cache

# Копирование исходного кода
COPY src/ ./src/

# Запуск приложения
CMD ["uv", "run", "python", "src/unified_memory_server.py"]
```

## 📦 Управление зависимостями

### Добавление новых пакетов
```bash
# Добавление runtime зависимости
uv add requests

# Добавление dev зависимости
uv add --dev pytest

# Добавление optional зависимости
uv add --optional monitoring prometheus-client
```

### Обновление зависимостей
```bash
# Обновление всех зависимостей
uv sync --upgrade

# Обновление конкретного пакета
uv add requests --upgrade

# Показать устаревшие пакеты
uv pip list --outdated
```

### Lock файл
```bash
# Создание lock файла
uv lock

# Установка из lock файла (для production)
uv sync --frozen
```

## 🚀 Использование в проекте

### 1. Разработка
```bash
# Клонирование и настройка
git clone <repo-url>
cd mcp-mem0

# Установка с UV (рекомендуется)
uv sync
uv run python src/unified_memory_server.py

# Или традиционный способ
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\activate   # Windows
pip install -e ".[dev]"
```

### 2. Production
```bash
# Установка только runtime зависимостей
uv sync --no-dev --frozen

# Запуск сервера
uv run python src/unified_memory_server.py
```

### 3. CI/CD
```yaml
# GitHub Actions example
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'

- name: Install UV
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Install dependencies
  run: uv sync --no-dev --frozen

- name: Run tests
  run: uv run pytest
```

## 🔍 Troubleshooting

### Проблемы с установкой
```bash
# Проверка версии UV
uv --version

# Очистка кэша
uv cache clean

# Полная переустановка окружения
rm -rf .venv uv.lock
uv sync
```

### Конфликты зависимостей
```bash
# Показать дерево зависимостей
uv pip show --files <package-name>

# Разрешение конфликтов
uv add <package> --resolution highest
```

## 📈 Сравнение производительности

```bash
# Тест установки всех зависимостей проекта:

# pip (традиционный)
time pip install -e ".[dev,monitoring,redis]"
# Результат: ~45 секунд

# UV (современный)
time uv sync
# Результат: ~3 секунды

# Улучшение: 15x быстрее! 🚀
```

## 💡 Best practices

1. **Всегда используйте uv.lock** для reproducible builds
2. **Используйте uv sync** вместо uv pip install для консистентности
3. **Добавляйте UV в Docker** для быстрых CI/CD pipeline
4. **Используйте uv run** для скриптов - не нужно активировать venv
5. **Регулярно обновляйте** uv до последней версии

## 🎯 Заключение

UV значительно ускоряет разработку Python проектов:
- ⚡ **15x быстрее** установка пакетов
- 🔒 **Lock файлы** для reproducible builds  
- 🛠️ **Лучший UX** с автоматическим управлением venv
- 🏗️ **Оптимизация CI/CD** pipeline

**Рекомендация**: Используйте UV для всех новых Python проектов! 