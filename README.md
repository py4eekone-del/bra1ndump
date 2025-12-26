# Digital Brain Dump

Интерактивная визуализация мыслей и воспоминаний в стиле "плавающих льдин".

## Структура

```
digital_brain_dump/
├── generator.py      # Генератор HTML из Telegram-экспорта
├── bot.py            # Telegram-бот с кнопкой WebApp
├── dist/             # Готовый билд для деплоя
│   ├── index.html
│   └── photos/       # Скопированные изображения
└── README.md
```

## Быстрый старт

### 1. Генерация сайта
```bash
python generator.py
```

### 2. Деплой на GitHub Pages
1. Создай репозиторий `digital_brain_dump` на GitHub
2. Загрузи содержимое папки `dist/`:
   ```bash
   cd dist
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/digital_brain_dump.git
   git push -u origin main
   ```
3. В настройках репо: Settings → Pages → Source: `main` branch
4. Через минуту сайт будет доступен: `https://YOUR_USERNAME.github.io/digital_brain_dump/`

### 3. Настройка бота
1. Создай бота через [@BotFather](https://t.me/BotFather)
2. Открой `bot.py` и замени:
   - `BOT_TOKEN` — токен от BotFather
   - `WEBAPP_URL` — URL с GitHub Pages
3. Установи зависимости:
   ```bash
   pip install python-telegram-bot
   ```

### 4. Запуск бота (Google Cloud / локально)
```bash
python bot.py
```

Для постоянной работы на сервере используй `tmux`:
```bash
tmux new -s brainbot
python bot.py
# Ctrl+B, затем D — выйти из сессии
```

## Хостинг

| Компонент | Где хостить | Стоимость |
|-----------|-------------|-----------|
| Сайт (HTML) | GitHub Pages | Бесплатно |
| Бот (Python) | Google Cloud VM (Always Free) | Бесплатно |

