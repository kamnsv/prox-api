# Используем Alpine-based Python image
FROM python:3.11-alpine

RUN apk add --no-cache ffmpeg

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt


# Открываем порт
EXPOSE 8000