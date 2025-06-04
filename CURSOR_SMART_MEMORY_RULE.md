# 🧠 CURSOR ПРАВИЛО: УМНАЯ ПАМЯТЬ АГЕНТА 

**Версия**: 2.0  
**Дата**: 2024-12-04  
**Цель**: Обеспечить агенту полную умную память с контекстом проектов

---

## 🎯 **ОСНОВНАЯ ФИЛОСОФИЯ**

**"Агент с памятью = Агент, который эволюционирует"**

Каждая сессия должна начинаться с восстановления контекста и заканчиваться обогащением памяти. Агент должен **ВСЕГДА** знать:
- Где мы сейчас в проекте
- Что уже решено и почему  
- Какие проблемы есть
- Что было попробовано раньше

---

## 📋 **ОБЯЗАТЕЛЬНЫЙ ПРОТОКОЛ СЕССИИ**

### **🔄 ФАЗА 1: ИНИЦИАЛИЗАЦИЯ ПАМЯТИ (ПЕРВЫЕ 30 СЕКУНД)**

```typescript
// 1. Определить проект
project_id = extract_project_from_context() || current_directory_name

// 2. Загрузить состояние проекта  
mcp_mem0_get_current_project_state({ project_id })

// 3. Получить релевантный контекст
mcp_mem0_get_accurate_context({ 
  query: user_request + " " + project_context,
  project_id,
  min_confidence: 7,
  limit: 8
})

// 4. Валидировать актуальность
mcp_mem0_validate_project_context({ project_id })
```

### **⚡ ФАЗА 2: АКТИВНАЯ РАБОТА (НЕПРЕРЫВНО)**

```typescript
// При каждом важном открытии/решении:
mcp_mem0_save_verified_memory({
  content: meaningful_discovery,
  project_id,
  category: auto_categorize(content), // architecture|problem|solution|status|decision  
  confidence_level: estimate_confidence(content),
  source: "coding_session",
  tags: extract_relevant_tags(content)
})

// При принятии архитектурных решений:
mcp_mem0_save_project_milestone({
  project_id,
  milestone_type: "architecture_decision", 
  content: decision_description,
  impact_level: 8
})

// При обнаружении противоречий:
mcp_mem0_resolve_context_conflict({
  conflicting_memory_ids: detected_conflicts,
  correct_content: new_accurate_info,
  resolution_reason: why_this_is_correct
})
```

### **📝 ФАЗА 3: ЗАВЕРШЕНИЕ СЕССИИ (ПОСЛЕДНИЕ 60 СЕКУНД)**

```typescript
// 1. Сохранить итоги сессии
mcp_mem0_save_project_milestone({
  project_id,
  milestone_type: "status_change",
  content: session_summary,
  impact_level: 6
})

// 2. Проверить качество новой информации  
mcp_mem0_audit_memory_quality({ project_id })

// 3. Обновить эволюцию проекта
mcp_mem0_track_project_evolution({ project_id })

// 4. Предложить следующие шаги
suggest_next_actions_based_on_memory()
```

---

## 🎨 **АВТОМАТИЧЕСКИЕ ТРИГГЕРЫ**

### **Сохранять в память ОБЯЗАТЕЛЬНО при:**
- ✅ Решении архитектурной задачи
- ✅ Обнаружении и исправлении бага
- ✅ Выборе между альтернативами
- ✅ Изменении важной конфигурации
- ✅ Принятии технического решения
- ✅ Обнаружении проблемы/ограничения

### **Запрашивать из памяти АВТОМАТИЧЕСКИ при:**
- 🔍 Первом упоминании проекта в сессии
- 🔍 Вопросах о прошлых решениях  
- 🔍 Попытке решить уже решенную проблему
- 🔍 Работе с незнакомым кодом
- 🔍 Планировании архитектуры

---

## 🏗 **КАТЕГОРИЗАЦИЯ ИНФОРМАЦИИ**

| Категория | Описание | Уровень доверия | Срок жизни |
|-----------|----------|-----------------|------------|
| `architecture` | Архитектурные решения | 8-10 | Долгосрочно |
| `problem` | Выявленные проблемы | 6-9 | До решения |
| `solution` | Найденные решения | 7-10 | Долгосрочно |
| `status` | Текущие статусы | 5-8 | Краткосрочно |
| `decision` | Принятые решения | 8-10 | Долгосрочно |

---

## 💡 **УМНЫЕ ПАТТЕРНЫ ИСПОЛЬЗОВАНИЯ**

### **Паттерн 1: "Поиск перед действием"**
```typescript
// ВСЕГДА перед решением проблемы:
const context = await mcp_mem0_get_accurate_context({
  query: problem_description,
  min_confidence: 6
})

if (context.found_solutions) {
  suggest_existing_solution(context)
} else {
  proceed_with_new_solution()
}
```

### **Паттерн 2: "Эволюционное обучение"**
```typescript
// После каждого значимого изменения:
await mcp_mem0_track_project_evolution({ 
  project_id,
  category: "solution" 
})

// Извлечь паттерны для будущих решений
const evolution = analyze_decision_patterns(evolution_data)
```

### **Паттерн 3: "Проактивная валидация"**
```typescript
// Каждые 20 минут активной работы:
const quality_report = await mcp_mem0_audit_memory_quality({ project_id })

if (quality_report.conflicts_detected) {
  resolve_conflicts_proactively()
}
```

---

## 🚨 **КРИТИЧЕСКИЕ ПРАВИЛА**

### **НИКОГДА НЕ:**
- ❌ Не начинать работу без загрузки контекста
- ❌ Не сохранять тривиальную информацию  
- ❌ Не игнорировать обнаруженные конфликты
- ❌ Не завершать сессию без обновления памяти

### **ВСЕГДА:**
- ✅ Проверять память перед новыми решениями
- ✅ Сохранять архитектурные решения
- ✅ Категоризировать информацию правильно
- ✅ Указывать реалистичный уровень доверия
- ✅ Разрешать конфликты немедленно

---

## 📊 **МЕТРИКИ ЭФФЕКТИВНОСТИ**

Отслеживать:
- 📈 Количество повторно использованных решений
- 📈 Время до нахождения релевантного контекста  
- 📈 Процент сессий с обновлением памяти
- 📉 Количество дублирующихся решений
- 📉 Время на решение уже решенных проблем

---

## 🔮 **РАСШИРЕННЫЕ ВОЗМОЖНОСТИ**

### **Мульти-проектная память:**
```typescript
// Поиск решений между проектами
const cross_project_context = await mcp_mem0_get_accurate_context({
  query: problem_description,
  // project_id не указываем для поиска везде
  min_confidence: 8
})
```

### **Предиктивные предложения:**
```typescript
// На основе эволюции проекта предложить следующие шаги
const evolution = await mcp_mem0_track_project_evolution({ project_id })
const suggestions = predict_next_logical_steps(evolution)
```

---

## 🎯 **ИТОГОВАЯ МАНТРА**

**"Каждая сессия обогащает память → Каждая новая сессия становится умнее → Агент эволюционирует с каждым проектом"**

---

*Правило активируется АВТОМАТИЧЕСКИ при каждом запуске Cursor в любом проекте с MCP mem0 инструментами.* 