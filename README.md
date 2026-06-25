https://github.com/user-attachments/assets/321883a9-2c62-44ac-9839-beda69643f1d

# Math Helper
<div align="center">

### Telegram-бот для решения математических задач с AI-помощником

Решение примеров, уравнений, неравенств, построение графиков, генерация похожих задач и пошаговых решений.

**Production-ready сервис с собственной монетизацией, системой ролей, CI/CD и LLM-интеграцией.**

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-blue)](https://docs.aiogram.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-red?logo=redis)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-enabled-blue?logo=docker)](https://docker.com/)
[![Coverage](https://img.shields.io/badge/Test_Coverage-70%25-brightgreen)](tests/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

### Попробовать

**Telegram:** https://t.me/math4students_bot

</div>

---

# Возможности

## Решение математических задач
Поддерживаются:

* Арифметические выражения
* Уравнения с переменной `x`
* Неравенства
* Вычисление сложных выражений
* Построение графиков функций
* Символьные вычисления через SymPy

### Примеры

```text
5 + 3
```

```text
2*x - 5 = 0
```

```text
x² - 4 > 0
```

```text
sin(x) / x
```

---

## AI-функции

Math Helper использует локальную LLM-инфраструктуру.

Пользователь может:

* Получить пошаговое решение задачи
* Сгенерировать похожие примеры
* Получить объяснение решения
* Улучшить понимание темы

Особенности:

* Ollama
* Локальная модель
* Приватное соединение через Tailscale
* Отсутствие зависимости от внешних AI API

---

## Freemium-модель

В проект встроена полноценная система монетизации через Telegram Stars.

### Бесплатный доступ

* Ограниченное количество запросов
* Автоматическое восстановление лимита через 24 часа

### Premium

* Безлимитное использование
* Доступ к AI-функциям
* Приоритетное обслуживание

Поддерживаемые тарифы:

| Период     | Стоимость |
| ---------- | --------- |
| 1 месяц    | 250 ⭐     |
| 3 месяца   | 650 ⭐     |
| 12 месяцев | 2500 ⭐    |

---

## 👥 Система ролей (RBAC)

В проекте реализована полноценная ролевая модель.

### User

* Решение задач
* История запросов

### Premium

* AI-возможности
* Повышенные лимиты

### Admin

* Работа с тикетами
* Блокировка пользователей
* Модерация

### Owner

* Управление администраторами
* Полный контроль системы

---

# Архитектура

Проект построен по принципам Clean Architecture.

```text
Telegram
    │
    ▼
Handlers
    │
    ▼
Services
    │
    ▼
Repositories
    │
    ▼
PostgreSQL
```

Дополнительно:

```text
Redis
├── Cache
├── FSM Storage
├── Rate Limiting
└── Temporary Data
```

---

# Production Features

Что реализовано как в реальном production-проекте:

✅ Clean Architecture

✅ Dependency Injection

✅ PostgreSQL + SQLAlchemy 2.0 Async

✅ Redis Caching

✅ Rate Limiting

✅ Cursor Pagination

✅ Docker

✅ Docker Compose

✅ Alembic Migrations

✅ GitHub Actions CI/CD

✅ Structured Logging

✅ Error Handling

✅ RBAC

✅ Unit Tests

✅ Integration Tests

✅ Linux VPS Deployment

---

# Демонстрация

> Скриншоты работы бота

<img width="371" height="587" alt="Screenshot_1" src="https://github.com/user-attachments/assets/50e6e28c-e147-4001-af0d-2bc749a0747f" />

<img width="374" height="871" alt="Screenshot_2" src="https://github.com/user-attachments/assets/069fc1ee-ecc4-4106-ac87-2993d73d10fa" />

<img width="372" height="826" alt="Screenshot_3" src="https://github.com/user-attachments/assets/75df662a-374f-4b6d-aa0b-71b63ddbc08f" />

<img width="369" height="680" alt="Screenshot_4" src="https://github.com/user-attachments/assets/b8d3f353-aa6b-429c-8144-53b0c3815ead" />

<img width="380" height="694" alt="Screenshot_5" src="https://github.com/user-attachments/assets/e0fccdfe-e154-4493-9e85-45605c3f6e7a" />

<img width="372" height="153" alt="Screenshot_6" src="https://github.com/user-attachments/assets/32e73fd3-84ed-4068-b1c9-c70dc0f772a9" />

<img width="373" height="363" alt="Screenshot_7" src="https://github.com/user-attachments/assets/882b67dd-511a-429c-b312-544854fcc6f7" />

---

# Быстрый старт

## Docker

```bash
git clone https://github.com/wqus/math_service.git

cd math_service

cp .env.example .env

docker compose up --build
```

---

## Локальный запуск

```bash
git clone https://github.com/wqus/math_service.git

cd math_service

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

alembic upgrade head

python run.py
```

---

# Тестирование

Покрытие проекта:

```text
70%+
```

Запуск тестов:

```bash
pytest
```

или

```bash
pytest --cov=src --cov-report=term-missing
```

---

# Технологический стек

### Backend

* Python 3.12
* aiogram 3.x
* AsyncIO
* SQLAlchemy 2.0 Async
* Pydantic v2

### Databases

* PostgreSQL
* Redis
* Alembic

### AI

* Ollama
* Local LLM
* Tailscale

### Infrastructure

* Docker
* Docker Compose
* GitHub Actions
* Linux VPS

### Testing

* Pytest
* Integration Tests
* Coverage

---

# Что было интересно реализовать

* Telegram Stars платежи
* Локальную LLM-инфраструктуру
* Rate Limiting через Redis
* Ticket System
* RBAC
* Cursor Pagination
* Полностью асинхронную архитектуру
* Автоматический CI/CD pipeline

---

# Contributions

Pull Requests приветствуются.

Если нашли баг или хотите предложить улучшение — создайте Issue.

---

# 📄 License

Проект распространяется под лицензией MIT.
