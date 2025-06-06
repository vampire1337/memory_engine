# 🔧 ПРИНУДИТЕЛЬНАЯ ПЕРЕСТРОЙКА DOCKER

## ❌ ПРОБЛЕМА: Docker использует старый кэш

Несмотря на исправления в коде, ошибка `embedding_dims` продолжается потому что **Docker использует старые закэшированные слои**.

```
2025-06-06 21:48:54 ERROR:__main__:❌ Ошибка создания Memory клиента: 'embedding_dims'
```

---

## 🚀 РЕШЕНИЕ: Полная очистка и пересборка

### Шаг 1: Остановить все контейнеры

```powershell
# Windows PowerShell
docker-compose -f docker-compose.unified.yml down
docker stop $(docker ps -aq)
```

### Шаг 2: Удалить ВСЕ связанное с проектом

```powershell
# Удалить контейнеры проекта
docker rm $(docker ps -aq --filter "name=unified-memory")

# Удалить образы проекта  
docker rmi $(docker images --filter "reference=*unified*" -q) -f
docker rmi $(docker images --filter "reference=*mem0*" -q) -f

# Удалить volumes проекта
docker volume rm $(docker volume ls --filter "name=unified" -q)
```

### Шаг 3: Очистить Docker build кэш

```powershell
# Очистить build кэш
docker builder prune -af

# Очистить все unused данные
docker system prune -af --volumes
```

### Шаг 4: Пересборка БЕЗ кэша

```powershell
# Пересборка с --no-cache
docker-compose -f docker-compose.unified.yml build --no-cache

# Запуск новых контейнеров
docker-compose -f docker-compose.unified.yml up -d
```

---

## ⚡ БЫСТРАЯ КОМАНДА (все в одном)

```powershell
# ПОЛНАЯ ОЧИСТКА И ПЕРЕСБОРКА

# 1. Остановить и удалить все
docker-compose -f docker-compose.unified.yml down
docker stop $(docker ps -aq) 2>$null
docker rm $(docker ps -aq) 2>$null
docker rmi $(docker images -q) -f 2>$null
docker volume rm $(docker volume ls -q) 2>$null
docker builder prune -af

# 2. Пересборка без кэша
docker-compose -f docker-compose.unified.yml build --no-cache

# 3. Запуск
docker-compose -f docker-compose.unified.yml up -d

# 4. Проверка через 30 секунд
Start-Sleep 30
docker-compose -f docker-compose.unified.yml logs memory-server
curl http://localhost:8051/health
```

---

## 🔍 ПРОВЕРКА РЕЗУЛЬТАТА

После пересборки должно быть:

```bash
✅ НЕТ ошибок embedding_dims в логах
✅ Сообщение "✅ Mem0 Memory клиент инициализирован"
✅ Health check возвращает 200
✅ Все контейнеры healthy
```

### Команды проверки:

```powershell
# Проверить логи
docker-compose -f docker-compose.unified.yml logs memory-server | Select-String "embedding_dims"
# Должно быть пусто

# Проверить health
curl http://localhost:8051/health
# Должно вернуть {"status":"healthy"}

# Проверить статус контейнеров
docker-compose -f docker-compose.unified.yml ps
```

---

## 🆘 ЕСЛИ ПРОБЛЕМА ОСТАЕТСЯ

### Дополнительная диагностика:

```powershell
# 1. Проверить какой именно файл utils.py копируется
docker-compose -f docker-compose.unified.yml exec memory-server ls -la /app/
docker-compose -f docker-compose.unified.yml exec memory-server head -50 /app/utils.py

# 2. Проверить содержимое utils.py в контейнере
docker-compose -f docker-compose.unified.yml exec memory-server grep -n "embedding_dims" /app/utils.py
# Должно быть пусто

# 3. Проверить Python импорты
docker-compose -f docker-compose.unified.yml exec memory-server python -c "
import sys
print('Python paths:')
for p in sys.path: print(f'  {p}')
"
```

### Если все еще ошибка - возможные причины:

1. **Старый utils.py в корне** - убедитесь что используется `src/utils.py`
2. **Кэш pip/Python** - в контейнере может быть кэш
3. **Версия Mem0** - возможно нужно обновить версию

---

## 📋 КОНТРОЛЬНЫЙ СПИСОК

- [ ] Остановлены все контейнеры
- [ ] Удалены все образы и volumes
- [ ] Очищен build кэш Docker
- [ ] Выполнена пересборка с `--no-cache`
- [ ] Проверены логи на отсутствие embedding_dims
- [ ] Health check возвращает 200
- [ ] Система работает без ошибок

---

**🎯 РЕЗУЛЬТАТ**: После принудительной пересборки ошибка `embedding_dims` должна исчезнуть навсегда.
