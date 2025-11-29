import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
# Импортируем Google GenAI
from google import genai
from google.genai.errors import APIError # Для обработки ошибок API

load_dotenv()

# Загружаем токены
TG_TOKEN = os.getenv("tg_token")
# !!! Изменено: Ключ для Gemini API. Убедись, что переменная в .env соответствует.
GEMINI_API_KEY = os.getenv("api_key") 

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

# Настраиваем логи
log_dir = "ChatGPT_Logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "error.log"),
    level=logging.ERROR,
    format="%(levelname)s: %(asctime)s %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S"
)

# Gemini клиент
# !!! Изменено: Инициализируем клиент Google GenAI
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    logging.error(f"Failed to initialize Gemini Client: {e}")
    # Желательно здесь как-то обработать критическую ошибку
    client = None 


# Функция генерации ответа
async def generate_response(prompt: str) -> str:
    if not client:
        return "Ошибка инициализации Gemini клиента. Проверь API ключ."
        
    # !!! Изменено: Используем метод generate_content для модели gemini-2.5-flash
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        # Получаем текст ответа
        return response.text
    except APIError as e:
        # Логируем ошибки API, например, невалидный ключ, лимиты и т.д.
        logging.error(f"Gemini API Error: {e}")
        return "Ошибка генерации ответа от Gemini API. Попробуй позже."
    except Exception as e:
        # Логируем другие ошибки
        logging.error(str(e))
        return "Ошибка генерации ответа. Попробуй позже."


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет!\nЯ Gemini 2.5 Telegram Bot 🤖\n" # !!! Обновлено приветствие
        "Задай мне любой вопрос — постараюсь помочь!"
    )


# Команда /bot
@dp.message(Command("bot"))
async def cmd_bot(message: types.Message):
    # Убедимся, что /bot не захватывает все команды
    prompt = message.text.replace("/bot", "", 1).strip()
    if not prompt:
        await message.answer("Напиши вопрос после команды /bot")
        return

    response = await generate_response(prompt)
    await message.answer(response)


# Обработка всех остальных сообщений
@dp.message()
async def handle_any_message(message: types.Message):
    # Добавим проверку на пустые сообщения, хотя aiogram обычно это обрабатывает
    if not message.text:
        return
        
    response = await generate_response(message.text)
    await message.answer(response)


# Запуск бота
async def main():
    print("Bot is running...")
    # Очищаем очередь, чтобы не обрабатывать старые сообщения
    await bot.delete_webhook(drop_pending_updates=True) 
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        # Убедись, что логгирование работает, если бот падает сразу
        if not os.path.exists(log_dir):
             os.makedirs(log_dir, exist_ok=True)
        # Более надежное логирование на случай падения asyncio.run
        with open(os.path.join(log_dir, "error.log"), "a") as f:
            f.write(f"FATAL ERROR: {e}\n")
        logging.error(f"FATAL ERROR: {e}")