# Базовый образ Python
FROM python:3.13-slim

# Отключаем создание .pyc файлов и буферизацию
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Копируем зависимости отдельно (для кеша)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Открываем порт (для webhook)
EXPOSE 8080

CMD ["python", "run.py"]
