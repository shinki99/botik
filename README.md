# 🔮 Бот для Гадания на Таро

Этот бот предназначен для автоматической отправки ежедневных гаданий на картах Таро в Telegram-канал.

## 📋 Требования к серверу

Минимальные:
- CPU: 4 ядра
- RAM: 8 GB
- SSD: 50 GB
- OS: Ubuntu Server 22.04 LTS

Оптимальные:
- CPU: 8 ядер
- RAM: 16 GB
- SSD: 100 GB
- OS: Ubuntu Server 22.04 LTS

## 🚀 Установка

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker и Docker Compose
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker

# Создание рабочей директории
mkdir -p ~/tarot_bot
cd ~/tarot_bot
```

### 2. Настройка бота

1. Создайте бота в Telegram через @BotFather и получите токен
2. Создайте канал в Telegram и добавьте бота как администратора
3. Получите ID канала (можно переслать сообщение из канала боту @getmyid_bot)

### 3. Подготовка файлов

1. Скопируйте все файлы проекта на сервер:
```bash
scp -r ./* user@your-server:~/tarot_bot/
```

2. Создайте файл `.env` для первого бота:
```bash
nano .env
```

Содержимое `.env`:
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=your_channel_id
```

3. Создайте файлы окружения для остальных ботов (.env.bot2, .env.bot3 и т.д.)

### 4. Запуск ботов

```bash
# Создание и запуск контейнеров
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

## 📝 Управление ботами

### Основные команды

```bash
# Запуск ботов
docker-compose up -d

# Остановка ботов
docker-compose down

# Перезапуск ботов
docker-compose restart

# Просмотр логов конкретного бота
docker-compose logs tarot-bot-1
```

### Мониторинг

```bash
# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats

# Просмотр логов в реальном времени
docker-compose logs -f
```

## 🔧 Настройка расписания

Бот отправляет сообщения в следующее время:
- 09:00 - Утреннее гадание
- 15:35 - Дневное гадание
- 15:40 - Дополнительное дневное гадание
- 18:00 - Вечернее гадание
- 23:00 - Ночное гадание

## ⚠️ Решение проблем

1. Если бот не отправляет сообщения:
   - Проверьте правильность токена и ID канала
   - Убедитесь, что бот имеет права администратора в канале
   - Проверьте логи: `docker-compose logs -f`

2. Если высокая нагрузка на сервер:
   - Проверьте использование ресурсов: `docker stats`
   - При необходимости измените ограничения в `docker-compose.yml`

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs -f`
2. Проверьте статус контейнеров: `docker-compose ps`
3. Убедитесь, что все переменные окружения установлены правильно

## 🔄 Обновление бота

```bash
# Остановка контейнеров
docker-compose down

# Обновление файлов бота
# (скопируйте новые файлы в директорию)

# Пересборка и запуск
docker-compose up -d --build
