FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Копирование файлов проекта
COPY requirements.txt .
COPY bot.py .
COPY tarot_data.py .
COPY .env .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Создание пользователя
RUN useradd -r -s /bin/false tarotbot
RUN mkdir -p /var/log/tarot_bot && chown tarotbot:tarotbot /var/log/tarot_bot

# Переключение на непривилегированного пользователя
USER tarotbot

# Запуск бота
CMD ["python", "bot.py"]
