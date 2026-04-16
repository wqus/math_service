https://github.com/user-attachments/assets/6bc34551-1dc5-44e9-a136-75b8bf8805fb


# Math Helper

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-7.0-blue)](https://core.telegram.org/bots/api)
[![Docker](https://img.shields.io/badge/Docker-✓-blue)](https://www.docker.com/)
[![License MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Асинхронный Telegram-бот для решения математических задач с интеграцией локальной LLM**

Поддерживает примеры, уравнения, неравенства, графики функций, генерацию похожих выражений и пошаговых объяснений через **Ollama**, freemium-модель и оплату Telegram Stars.

---
## Оглавление
- [Возможности](#-возможности)
- [Демонстрация](#-демонстрация)
- [Быстрый старт для пользователя](#-быстрый-старт-для-пользователя)
- [Установка и запуск для разработчика](#-установка-и-запуск-для-разработчика)
- [Примеры использования](#-примеры-использования)
- [Конфигурация](#-конфигурация)
- [Команды бота](#-команды-бота)
- [Технологии](#-технологии)
- [Структура проекта](#-структура-проекта)
- [Тестирование и линтинг](#-тестирование-и-линтинг)
- [Планы развития](#-планы-развития)
- [Участие в разработке](#-участие-в-разработке)
- [Лицензия](#-лицензия)

---
## Возможности

### Математические функции
- Решение арифметических примеров, уравнений с одной переменной и одномерных неравенств
- Построение графиков функций (SymPy + Matplotlib)
- **Генерация похожих выражений и пошаговых объяснений решений** через локальную LLM (Ollama)

### Дополнительно
- История запросов с постраничной навигацией
- Freemium-модель + премиум-подписка через Telegram Stars
- Система поддержки (тикеты SUP-XXXX)
- Двуязычность (RU / EN)
- Полноценный RBAC (user / admin / owner)
---

## Демонстрация
<img width="371" height="587" alt="Screenshot_1" src="https://github.com/user-attachments/assets/50e6e28c-e147-4001-af0d-2bc749a0747f" />
<img width="374" height="871" alt="Screenshot_2" src="https://github.com/user-attachments/assets/069fc1ee-ecc4-4106-ac87-2993d73d10fa" />
<img width="372" height="826" alt="Screenshot_3" src="https://github.com/user-attachments/assets/75df662a-374f-4b6d-aa0b-71b63ddbc08f" />
<img width="369" height="680" alt="Screenshot_4" src="https://github.com/user-attachments/assets/b8d3f353-aa6b-429c-8144-53b0c3815ead" />
<img width="380" height="694" alt="Screenshot_5" src="https://github.com/user-attachments/assets/e0fccdfe-e154-4493-9e85-45605c3f6e7a" />
<img width="372" height="153" alt="Screenshot_6" src="https://github.com/user-attachments/assets/32e73fd3-84ed-4068-b1c9-c70dc0f772a9" />
<img width="373" height="363" alt="Screenshot_7" src="https://github.com/user-attachments/assets/882b67dd-511a-429c-b312-544854fcc6f7" />
<img width="385" height="662" alt="image" src="https://github.com/user-attachments/assets/fe1872ff-afb3-49d7-9ac1-756e287da609" />


## Быстрый старт для пользователя

1. Найдите бота в Telegram: **[@math4students_bot](https://t.me/math4students_bot)** 
2. Отправьте `/start` и выберите язык (RU / EN)
3. Используйте команды или текстовые запросы:

| Что сделать              | Команда / текст                  |
|--------------------------|----------------------------------|
| Решить пример            | `5+3` или `2*8-1`                |
| Решить уравнение         | `2*x + 5 = 0`                    |
| Решить неравенство       | `x^2 - 5x + 6 > 0`               |
| Построить график         | `График📈` → ввести функцию      |
| Показать историю         | `История📖` / `History📖`        |
| Премиум                  | `Премиум🧠` / `Premium🧠`        |
| Поддержка                | `Поддержка✉` / `Support✉`        |

---

## Установка и запуск для разработчика

### Требования
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker и Docker Compose (опционально)

### 1. Клонирование репозитория
```bash
git clone https://github.com/wqus/math_service.git
cd math_service
2. Настройка окружения
bash
cp .env.example .env
# Отредактируйте .env (см. раздел Конфигурация)
3. Запуск через Docker (рекомендуется)
bash
docker-compose up --build
# Для фонового режима: docker-compose up -d
4. Локальный запуск (без Docker)
bash
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
alembic upgrade head
python run.py

## Примеры использования

## Примеры использования

| Ввод пользователя                      | Ответ бота |
|----------------------------------------|------------|
| `5+3`                                  | `8` |
| `2*x - 5 = 0`                          | `x = 2.5` |
| `x^2 - 4 > 0`                          | `(-∞, -2) ∪ (2, ∞)` |
| `График📈 sin(x)/x`                    | Изображение графика на [-10, 10] |
| `История📖`                            | Список последних запросов с ответами |
| `Примечание📃`                         | Правила записи (умножение *, степень ** или ^, градусы в скобках) |
| `Премиум🧠`                            | Меню выбора подписки за Telegram Stars |
| `Показать решение`                     | LLM генерирует пошаговое объяснение |
| `Сгенерировать похожее`                | LLM генерирует 3–5 похожих выражений |

⚙️ Конфигурация
Файл .env содержит следующие переменные:

Переменная	Описание
MODE=

TOKEN=

LOCAL_WEBHOOK_HOST=
LOCAL_WEBHOOK_PORT=

WEBHOOK_PATH=
WEBHOOK_BASE_URL=

REDIS_HOST =

POSTGRES_HOST=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_USER=

Команды бота
Бот понимает как команды со слешем, так и текстовые сообщения на русском/английском.

Команда (RU)	Команда (EN)	Описание
/start	/start	Приветствие и выбор языка
Умения🤓	Skills🤓	Список решаемых типов задач
Примечание📃	Note📃	Правила записи выражений
График📈	Plot📈	Запуск построения графика
История📖	History📖	Показать историю запросов
Премиум🧠	Premium🧠	Информация о подписке и покупка
Поддержка✉	Support✉	Отправить сообщение в поддержку
Любое выражение	–	Автоматическое решение (пример, уравнение, неравенство)

Команды для админов:
/ban
/bans_history
/tickets

Команда для владельца:
/add_admin
/remove_admin

callback - команды:
unban
ответ на тикет

## Технологии
- **Python 3.11+**
- **aiogram 3.x** — асинхронный фреймворк
- **PostgreSQL + SQLAlchemy 2.0** + Alembic
- **Redis** — FSM, rate limiting, кэширование
- **Ollama** + локальная LLM — генерация похожих задач и объяснений
- **SymPy / NumPy / Matplotlib** — точная математика и графики
- **Docker + GitHub Actions** — CI/CD и zero-downtime деплой

📁 Структура проекта
text
math_service/
├── bot/
│   ├── handlers/            # Обработчики команд и текстовых сообщений
│   ├── services/            # Бизнес-логика: решение, графики, платежи
│   ├── repositories/        # Работа с БД (пользователи, история, тикеты)
│   ├── database/            # SQLAlchemy модели, сессии
│   ├── middlewares/         # i18n, антиспам, логирование
│   ├── keyboards/           # Inline и Reply клавиатуры
│   ├── states/              # FSM состояния (для графиков, поддержки)
│   └── locales/             # Файлы переводов (RU/EN)
├── alembic/                 # Миграции Alembic
├── .github/workflows/       # CI/CD (GitHub Actions)
├── tests/                   # Тесты (планируется)
├── run.py                   # Точка входа
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── requirements.txt

Тестирование и линтинг
Раздел будет дополнен после внедрения тестов и нагрузочного тестирования.

Планируемый стек:

pytest + pytest-asyncio – модульные и интеграционные тесты

locust / k6 – нагрузочное тестирование

black / isort – форматирование

flake8 / ruff – статический анализ

Пример команд (после реализации):

bash
pytest tests/                    # все тесты
pytest tests/test_math_solver.py
black bot/ --check
flake8 bot/

 Планы развития

🔜 Модульные и интеграционные тесты (покрытие >80%)

🔜 Нагрузочное тестирование (проверка под высоким RPS)

🔜 Обёртка в FastAPI (REST API для внешних сервисов)

 Участие в разработке
Чтобы предложить улучшение:

Сделайте fork репозитория

Создайте ветку: git checkout -b feature/ваша-идея

Внесите изменения и сделайте коммиты (следуйте Conventional Commits)

Запушьте ветку: git push origin feature/ваша-идея

Откройте Pull Request в ветку main

Пожалуйста, ознакомьтесь с CONTRIBUTING.md и CODE_OF_CONDUCT.md (будут добавлены).

📄 Лицензия
Проект распространяется под лицензией MIT. Подробности в файле LICENSE.
