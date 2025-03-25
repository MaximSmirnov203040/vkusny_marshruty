# Vkusny Marshruty - Система продажи горящих путевок

Комплексное решение для продажи горящих путевок, включающее:
- Telegram бот для сбора заявок
- Веб-сайт с каталогом путевок
- Административную панель
- Систему управления заявками

## Требования к системе

- Python 3.8 или выше
- PostgreSQL 12 или выше
- Git
- Docker (опционально, для контейнеризации)

## Установка и настройка

### 1. Подготовка окружения

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/vkusny_marshruty.git
cd vkusny_marshruty
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

### 2. Настройка базы данных

1. Создайте базу данных PostgreSQL:
```bash
createdb vkusny_marshruty
```

2. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

3. Отредактируйте файл `.env`, заполнив все необходимые переменные:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/vkusny_marshruty
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_GROUP_ID=your_group_id_here
SECRET_KEY=your_secret_key_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
```

### 3. Инициализация базы данных

1. Примените миграции:
```bash
alembic upgrade head
```

### 4. Запуск приложения

1. Запустите сервер разработки:
```bash
uvicorn app.main:app --reload
```

Приложение будет доступно по адресу: http://localhost:8000

## Развертывание на сервере

### 1. Подготовка сервера

1. Установите необходимые пакеты:
```bash
sudo apt update
sudo apt install python3.8 python3.8-venv postgresql postgresql-contrib nginx
```

2. Настройте PostgreSQL:
```bash
sudo -u postgres psql
CREATE DATABASE vkusny_marshruty;
CREATE USER vkusny_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE vkusny_marshruty TO vkusny_user;
\q
```

### 2. Развертывание приложения

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/vkusny_marshruty.git
cd vkusny_marshruty
```

2. Создайте и активируйте виртуальное окружение:
```bash
python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Создайте и настройте файл `.env`:
```bash
cp .env.example .env
# Отредактируйте .env файл с правильными настройками
```

4. Примените миграции:
```bash
alembic upgrade head
```

### 3. Настройка systemd

1. Создайте файл сервиса:
```bash
sudo nano /etc/systemd/system/vkusny.service
```

2. Добавьте следующее содержимое:
```ini
[Unit]
Description=Vkusny Marshruty Application
After=network.target

[Service]
User=your_user
Group=your_group
WorkingDirectory=/path/to/vkusny_marshruty
Environment="PATH=/path/to/vkusny_marshruty/venv/bin"
ExecStart=/path/to/vkusny_marshruty/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

3. Запустите сервис:
```bash
sudo systemctl start vkusny
sudo systemctl enable vkusny
```

### 4. Настройка Nginx

1. Создайте конфигурацию Nginx:
```bash
sudo nano /etc/nginx/sites-available/vkusny
```

2. Добавьте следующее содержимое:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. Активируйте конфигурацию:
```bash
sudo ln -s /etc/nginx/sites-available/vkusny /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Использование системы

### Административная панель

1. Откройте http://your_domain.com/admin
2. Войдите с учетными данными администратора
3. Управляйте турами и заявками через веб-интерфейс

### Telegram бот

1. Найдите бота в Telegram по имени @your_bot_name
2. Используйте команды:
   - /start - Начало работы
   - /help - Список команд
   - /tours - Список всех туров
   - /hot - Горящие предложения

### API

API документация доступна по адресу: http://your_domain.com/docs

## Безопасность

1. Регулярно обновляйте зависимости:
```bash
pip install -r requirements.txt --upgrade
```

2. Меняйте пароли администратора и базы данных каждые 3 месяца
3. Настройте SSL-сертификат для HTTPS
4. Регулярно делайте резервные копии базы данных

## Поддержка

При возникновении проблем:
1. Проверьте логи приложения: `sudo journalctl -u vkusny`
2. Проверьте логи Nginx: `sudo tail -f /var/log/nginx/error.log`
3. Проверьте логи PostgreSQL: `sudo tail -f /var/log/postgresql/postgresql-*.log`

## Обновление системы

1. Остановите сервис:
```bash
sudo systemctl stop vkusny
```

2. Обновите код:
```bash
git pull origin main
```

3. Обновите зависимости:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

4. Примените миграции:
```bash
alembic upgrade head
```

5. Запустите сервис:
```bash
sudo systemctl start vkusny
```

## Структура проекта

```
vkusny_marshruty/
├── app/
│   ├── api/            # API endpoints
│   ├── bot/            # Telegram bot
│   ├── core/           # Core functionality
│   ├── db/             # Database models
│   ├── schemas/        # Pydantic schemas
│   └── templates/      # HTML templates
├── alembic/            # Database migrations
├── static/             # Static files
└── tests/              # Tests
```

## Технологии

- Python 3.8+
- FastAPI
- SQLAlchemy
- Alembic
- Python-telegram-bot
- PostgreSQL
- Docker (для контейнеризации) 