# Установка образа Alpine Linux содержащего Python 3.10.11 из DockerHub
FROM python:3.13-alpine

# Запускаем команду pip install для всех необходимых библиотек
RUN pip install --upgrade pip \
    && pip install python-dotenv \
    && pip install aiogram \
    && pip install google-genai

# Создаем рабочую директорию с ботом внутри контейнера
WORKDIR /opt/Gemini