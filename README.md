# Вкусные Маршруты (Vkusny Marshruty)

Телеграм-бот для управления туристическими маршрутами и заявками на туры.

## Функциональность

- Создание и управление турами
- Обработка заявок на участие в турах
- Административная панель для управления турами и заявками
- API для интеграции с внешними системами

## Технологии

- Python 3.8+
- FastAPI
- SQLAlchemy
- python-telegram-bot
- PostgreSQL
- Pydantic

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/vkusny_marshruty.git
cd vkusny_marshruty
```

2. Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
pip install -r requirements.txt
```

3. Создайте файл .env на основе .env.example и заполните необходимые переменные окружения:
```bash
cp .env.example .env
```

4. Создайте базу данных PostgreSQL:
```bash
createdb vkusny_marshruty
```

5. Примените миграции:
```bash
alembic upgrade head
```

## Запуск

1. Запустите API:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. В отдельном терминале запустите бота:
```bash
python -m app.bot.run
```

## Переменные окружения

Создайте файл `.env` со следующими переменными:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/vkusny_marshruty
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_GROUP_ID=your_group_id
ADMIN_IDS=id1,id2
SECRET_KEY=your_secret_key
API_URL=http://localhost:8000
```

## Разработка

1. Установите pre-commit хуки:
```bash
pre-commit install
```

2. Запустите тесты:
```bash
pytest
```

## Лицензия

MIT 