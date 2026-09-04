# Запуск

## Требования

- Docker + Docker Compose
- Аккаунт на [sibsutis.ru](https://sibsutis.ru) (логин/пароль)
- Telegram-бот (токен от [@BotFather](https://t.me/BotFather))

## Быстрый старт

1. Склонировать репозиторий и создать `.env`:

```bash
git clone <repo-url>
cd sibsutis-schedule
cp .env.example .env
```

2. Заполнить `.env`:

| Переменная | Описание |
|---|---|
| `SIBSUTIS_LOGIN` | Логин от sibsutis.ru |
| `SIBSUTIS_PASSWORD` | Пароль от sibsutis.ru |
| `BOT_TOKEN` | Токен Telegram-бота |
| `BOT_ADMIN_IDS` | ID админов, например `[123456789,987654321]` |
| `DB_HOST` | Хост PostgreSQL (в Docker: `postgres`) |
| `DB_PORT` | Порт PostgreSQL (`5432`) |
| `DB_USER` | Пользователь БД |
| `DB_PASSWORD` | Пароль БД |
| `DB_NAME` | Имя базы данных |

3. Запустить:

```bash
docker compose up -d
```


## Обновление

```bash
git pull
docker compose up -d --build
```