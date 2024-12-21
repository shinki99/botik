#!/bin/bash

# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3 python3-pip python3-venv supervisor

# Создание пользователя для бота
sudo useradd -r -s /bin/false tarotbot

# Создание директории для бота
sudo mkdir -p /opt/tarot_bot
sudo chown tarotbot:tarotbot /opt/tarot_bot

# Копирование файлов бота
sudo cp -r ./* /opt/tarot_bot/
sudo chown -R tarotbot:tarotbot /opt/tarot_bot/

# Создание виртуального окружения
cd /opt/tarot_bot
sudo -u tarotbot python3 -m venv venv
sudo -u tarotbot ./venv/bin/pip install -r requirements.txt

# Установка systemd сервиса
sudo cp tarot-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tarot-bot
sudo systemctl start tarot-bot

# Настройка логирования
sudo mkdir -p /var/log/tarot_bot
sudo chown tarotbot:tarotbot /var/log/tarot_bot

echo "Установка завершена!"
