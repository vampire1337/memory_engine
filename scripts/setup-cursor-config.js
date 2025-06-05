#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');

function getCursorConfigPath() {
  const platform = os.platform();
  const homeDir = os.homedir();
  
  switch (platform) {
    case 'win32':
      return path.join(homeDir, 'AppData', 'Roaming', 'Cursor', 'User', 'globalStorage', 'cursor.claude-desktop', 'claude_desktop_config.json');
    case 'darwin':
      return path.join(homeDir, 'Library', 'Application Support', 'Cursor', 'User', 'globalStorage', 'cursor.claude-desktop', 'claude_desktop_config.json');
    case 'linux':
      return path.join(homeDir, '.config', 'Cursor', 'User', 'globalStorage', 'cursor.claude-desktop', 'claude_desktop_config.json');
    default:
      throw new Error(`Неподдерживаемая платформа: ${platform}`);
  }
}

// Правильная конфигурация для FastAPI-MCP через SSE
const mcpConfig = {
  "mcpServers": {
    "fastapi-mem0-memory": {
      "transport": "sse",
      "url": "http://localhost:8000/mcp",
      "name": "FastAPI Mem0 Memory Server",
      "description": "Стабильный сервер памяти с 11 инструментами"
    }
  }
};

function main() {
  console.log('🔧 НАСТРОЙКА CURSOR MCP (SSE Transport)');
  console.log('='.repeat(50));
  
  try {
    const configPath = getCursorConfigPath();
    console.log(`📁 Путь к конфигурации: ${configPath}`);
    
    // Создаем директорию если не существует
    const configDir = path.dirname(configPath);
    if (!fs.existsSync(configDir)) {
      fs.mkdirSync(configDir, { recursive: true });
    }
    
    let finalConfig = mcpConfig;
    
    // Если файл существует, объединяем конфигурации
    if (fs.existsSync(configPath)) {
      console.log('📋 Найдена существующая конфигурация');
      
      // Создаем бэкап
      const backupPath = configPath + '.backup';
      fs.copyFileSync(configPath, backupPath);
      console.log(`✅ Создан бэкап: ${backupPath}`);
      
      try {
        const existingConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        finalConfig = { ...existingConfig };
        
        if (!finalConfig.mcpServers) {
          finalConfig.mcpServers = {};
        }
        
        finalConfig.mcpServers['fastapi-mem0-memory'] = mcpConfig.mcpServers['fastapi-mem0-memory'];
        
        console.log('🔄 Конфигурации объединены');
      } catch (error) {
        console.log('⚠️  Ошибка чтения существующей конфигурации, создаем новую');
        finalConfig = mcpConfig;
      }
    } else {
      console.log('📝 Создаем новую конфигурацию');
    }
    
    // Сохраняем конфигурацию
    fs.writeFileSync(configPath, JSON.stringify(finalConfig, null, 2));
    
    console.log('✅ Конфигурация Cursor MCP обновлена!');
    console.log('');
    console.log('📋 Добавленный сервер:');
    console.log('   • Название: FastAPI Mem0 Memory Server');
    console.log('   • Транспорт: SSE (Server-Sent Events)');
    console.log('   • URL: http://localhost:8000/mcp');
    console.log('   • Инструменты: 11 функций памяти');
    console.log('');
    console.log('🚀 Что дальше:');
    console.log('   1. Запустите сервер: npm run server');
    console.log('   2. Убедитесь что сервер доступен: http://localhost:8000');
    console.log('   3. Перезапустите Cursor IDE');
    console.log('   4. Проверьте инструменты памяти в Claude');
    
  } catch (error) {
    console.error(`❌ Ошибка настройки: ${error.message}`);
    console.log('');
    console.log('🔧 Альтернативная настройка через npx:');
    console.log('   Добавьте в Cursor config:');
    console.log('   "fastapi-mem0-memory": {');
    console.log('     "command": "npx",');
    console.log('     "args": ["mcp-remote", "http://localhost:8000/mcp"]');
    console.log('   }');
    process.exit(1);
  }
}

if (require.main === module) {
  main();
} 