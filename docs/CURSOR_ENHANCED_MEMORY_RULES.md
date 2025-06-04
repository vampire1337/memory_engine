# 🚀 УЛЬТИМАТИВНЫЕ ПРАВИЛА CURSOR - ENHANCED MEMORY SYSTEM MCP

## 🎯 MASTER RULE - ТОЧНОСТЬ ПРЕВЫШЕ ВСЕГО

**ЗОЛОТОЕ ПРАВИЛО**: Неточный контекст хуже отсутствия контекста. Всегда проверяй качество информации перед использованием.

---

## 📋 ОБЯЗАТЕЛЬНЫЙ WORKFLOW ДЛЯ КАЖДОГО ПРОЕКТА

### ЭТАП 1: ИНИЦИАЛИЗАЦИЯ ПРОЕКТА (При первом подключении)

```workflow
1. audit_memory_quality() - проверить общее состояние базы
2. validate_project_context(project_id) - аудит конкретного проекта  
3. get_current_project_state(project_id) - понять текущее состояние
4. Если есть конфликты -> resolve_context_conflict()
```

### ЭТАП 2: ПЕРЕД КАЖДЫМ РЕШЕНИЕМ (Обязательно!)

```workflow
1. get_accurate_context(query, project_id, min_confidence=7) - ТОЛЬКО точная информация
2. validate_project_context(project_id) - быстрая проверка актуальности
3. Принимать решения ТОЛЬКО на основе проверенного контекста
```

### ЭТАП 3: ПОСЛЕ КАЖДОГО ВАЖНОГО ДЕЙСТВИЯ

```workflow
1. save_verified_memory() или save_project_milestone() - зафиксировать результат
2. Указать правильный confidence_level (1-10)
3. Добавить источник и категорию
4. Проверить на конфликты автоматически
```

---

## 🛠️ SMART USAGE PATTERNS - МАКСИМАЛЬНАЯ ЭФФЕКТИВНОСТЬ

### 💎 PATTERN 1: АРХИТЕКТУРНЫЕ РЕШЕНИЯ

```
ВСЕГДА используй save_project_milestone() для:
✅ architecture_decision - архитектурные решения
✅ problem_identified - выявленные проблемы  
✅ solution_implemented - реализованные решения
✅ status_change - изменения статуса

ПАРАМЕТРЫ:
- impact_level: 8-10 для critical решений
- tags: детальные теги для поиска
- project_id: ВСЕГДА указывай проект
```

### 💎 PATTERN 2: ПОИСК ИНФОРМАЦИИ

```
ПРИОРИТЕТ ИНСТРУМЕНТОВ:
1. get_accurate_context() - для production decisions
2. get_current_project_state() - для обзора проекта
3. search_memories() - только для общего поиска
4. get_all_memories() - ИЗБЕГАЙ (слишком много noise)

НАСТРОЙКИ:
- min_confidence: 7+ для важных решений
- project_id: ВСЕГДА фильтруй по проекту
- limit: 3-5 для фокуса, 10+ для исследования
```

### 💎 PATTERN 3: QUALITY CONTROL

```
ЕЖЕДНЕВНО (в начале работы):
1. audit_memory_quality(project_id) - health check проекта
2. Если health_score < 70 -> немедленный cleanup
3. validate_project_context() - проверка конфликтов

ЕЖЕНЕДЕЛЬНО:
1. audit_memory_quality() - полный аудит базы
2. track_project_evolution() - анализ прогресса
3. Cleanup expired и deprecated записей
```

---

## ⚡ CONFIDENCE LEVEL SYSTEM - ИСПОЛЬЗУЙ ПРАВИЛЬНО

### КРИТЕРИИ CONFIDENCE SCORING:

```
10 (МАКСИМУМ) - Проверенные факты, code analysis, официальная документация
9  (ОЧЕНЬ ВЫСОКИЙ) - Архитектурные решения, confirmed by tests
8  (ВЫСОКИЙ) - Решения команды, code review findings
7  (ХОРОШИЙ) - User feedback, documentation research  
6  (СРЕДНИЙ+) - Предположения на основе опыта
5  (СРЕДНИЙ) - Гипотезы, требуют проверки
4  (НИЗКИЙ+) - Неподтвержденные идеи
3  (НИЗКИЙ) - Догадки, speculation
2  (ОЧЕНЬ НИЗКИЙ) - Неопределенная информация
1  (МИНИМУМ) - Сомнительная информация
```

### ПРАВИЛА ИСПОЛЬЗОВАНИЯ:

- **Confidence 8+**: Можно использовать для production решений
- **Confidence 5-7**: Требует дополнительной проверки
- **Confidence <5**: НЕ использовать для важных решений

---

## 🔥 ADVANCED EFFICIENCY RULES

### RULE 1: SMART CATEGORIZATION

```
ОБЯЗАТЕЛЬНЫЕ КАТЕГОРИИ:
- architecture: компоненты, технологии, паттерны
- problem: баги, ограничения, технический долг
- solution: фиксы, улучшения, оптимизации  
- status: прогресс, milestones, состояние
- decision: принятые решения и их reasoning

ВСЕГДА указывай правильную категорию!
```

### RULE 2: EXPIRATION STRATEGY

```
ВРЕМЯ ЖИЗНИ ПО ТИПАМ:
- architecture: expires_in_days=180 (стабильно)
- status: expires_in_days=30 (быстро меняется)
- problem: expires_in_days=90 (средняя скорость)
- solution: expires_in_days=120 (относительно стабильно)
- decision: expires_in_days=365 (долгосрочно)

НЕ УКАЗЫВАЙ expiration для permanent информации!
```

### RULE 3: CONFLICT RESOLUTION PRIORITY

```
ПРИ ОБНАРУЖЕНИИ КОНФЛИКТА:
1. НЕМЕДЛЕННО останови работу
2. Проанализируй conflicting информацию
3. Выбери ПРАВИЛЬНУЮ версию на основе:
   - Источника (code > docs > assumptions)
   - Времени (newer > older для status/problems)  
   - Confidence level (higher > lower)
4. resolve_context_conflict() с детальным reasoning
5. ТОЛЬКО ПОСЛЕ разрешения продолжай работу
```

---

## 🎖️ EXPERT LEVEL OPTIMIZATIONS

### OPTIMIZATION 1: BATCH OPERATIONS

```
ДЛЯ МНОЖЕСТВЕННЫХ ОПЕРАЦИЙ:
1. Сначала get_current_project_state() - полный контекст
2. Планируй все save операции
3. Выполняй save операции в порядке важности
4. Финальный validate_project_context() для проверки
```

### OPTIMIZATION 2: INTELLIGENT TAGGING

```
SMART TAGS СИСТЕМА:
- Технологии: react, postgresql, redis, docker
- Компоненты: frontend, backend, database, auth
- Статус: completed, in-progress, planned, blocked
- Приоритет: critical, high, medium, low
- Тип: bug, feature, optimization, refactor

ВСЕГДА добавляй 3-5 relevant тегов!
```

### OPTIMIZATION 3: EVOLUTION TRACKING

```
ДЛЯ ДОЛГОСРОЧНЫХ ПРОЕКТОВ:
1. track_project_evolution() - еженедельно
2. Анализируй deprecated_entries для learning
3. Изучай decision patterns для optimization
4. Используй evolution для predictive planning
```

---

## ⚠️ CRITICAL ERROR PREVENTION

### НИКОГДА НЕ ДЕЛАЙ:

❌ **save_memory()** без confidence_level и project_id  
❌ **search_memories()** для critical decisions (используй get_accurate_context)  
❌ Ignore конфликты - ВСЕГДА разрешай немедленно  
❌ Сохранение с confidence < 5 для production информации  
❌ Пропуск validation перед важными решениями  
❌ Смешивание проектов в одном project_id  

### ВСЕГДА ДЕЛАЙ:

✅ **get_accurate_context()** перед каждым решением  
✅ **validate_project_context()** при подозрении на конфликты  
✅ **audit_memory_quality()** для health monitoring  
✅ Указывай source для audit trail  
✅ Используй appropriate expiration для time-sensitive данных  
✅ Разрешай конфликты с detailed reasoning  

---

## 🏆 PERFORMANCE METRICS TO TRACK

### DAILY METRICS:
- Health Score проекта (target: >85)
- Количество конфликтов (target: 0)
- Средний confidence level (target: >7)

### WEEKLY METRICS:
- Evolution timeline consistency
- Deprecated entries ratio (target: <10%)
- Response time для get_accurate_context (target: <2s)

---

## 🚀 EMERGENCY PROTOCOLS

### ЕСЛИ HEALTH SCORE < 50:
1. СТОП всех операций
2. audit_memory_quality() - детальный анализ
3. Массовая очистка expired/deprecated
4. resolve_context_conflict() для всех конфликтов
5. Возобновление только после health_score > 70

### ЕСЛИ КРИТИЧЕСКИЙ КОНФЛИКТ:
1. Блокировка новых save операций
2. get_accurate_context() для понимания impact
3. Ручное разрешение с экспертным input
4. Validation всего related контекста

---

## 💡 WORKFLOW AUTOMATION COMMANDS

### MORNING ROUTINE:
```bash
audit_memory_quality(project_id="current_project")
validate_project_context("current_project") 
get_current_project_state("current_project")
```

### BEFORE CRITICAL DECISION:
```bash
get_accurate_context(query, project_id, min_confidence=8)
validate_project_context(project_id)
```

### AFTER IMPORTANT WORK:
```bash
save_project_milestone() или save_verified_memory()
validate_project_context(project_id)
```

---

## 🎯 SUCCESS MANTRAS

1. **"КАЧЕСТВО ПРЕВЫШЕ СКОРОСТИ"** - лучше медленно и правильно
2. **"КОНФЛИКТЫ = КРИТИЧЕСКАЯ ОШИБКА"** - разрешай немедленно  
3. **"КОНТЕКСТ = РЕШЕНИЕ"** - всегда проверяй перед действием
4. **"ДОВЕРЯЙ, НО ПРОВЕРЯЙ"** - confidence level не гарантия
5. **"ЭВОЛЮЦИЯ = ОБУЧЕНИЕ"** - используй историю для роста

---

**РЕЗУЛЬТАТ: При следовании этим правилам ты получишь систему памяти с 99%+ точностью контекста и максимальной эффективностью принятия решений.** 