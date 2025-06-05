import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from deepseek_api import DeepSeekAPI

# Функция для загрузки переменных из .env файла
def load_env_vars():
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"\'')
    except FileNotFoundError:
        pass
    return env_vars

# Загрузка переменных окружения
env_vars = load_env_vars()
TG_TOKEN = env_vars.get('TG_TOKEN') or os.getenv('TG_TOKEN')
DEEPSEEK_API_KEY = env_vars.get('DEEPSEEK_API_KEY') or os.getenv('DEEPSEEK_API_KEY')

if not TG_TOKEN or not DEEPSEEK_API_KEY:
    missing = []
    if not TG_TOKEN: missing.append('TG_TOKEN')
    if not DEEPSEEK_API_KEY: missing.append('DEEPSEEK_API_KEY')
    raise ValueError(f"Не установлены обязательные переменные: {', '.join(missing)}")

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Инициализация бота с новым синтаксисом
bot = Bot(
    token=TG_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
deepseek = DeepSeekAPI(api_key=DEEPSEEK_API_KEY)

# Хранение контекста разговора
user_conversations = {}

class Conversation:
    def __init__(self):
        self.messages = []
    
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
    
    def get_messages(self):
        return self.messages.copy()

@dp.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    user_conversations[user_id] = Conversation()
    await message.answer("Привет! Я бот на основе DeepSeek AI.\nЗадай мне любой вопрос, и я постараюсь ответить.")

@dp.message(Command("new"))
async def new_conversation_handler(message: Message):
    user_id = message.from_user.id
    user_conversations[user_id] = Conversation()
    await message.answer("Начинаем новый диалог. Контекст предыдущего разговора очищен.")

@dp.message()
async def message_handler(message: Message):
    user_id = message.from_user.id
    
    # Если у пользователя нет активного диалога, создаем новый
    if user_id not in user_conversations:
        user_conversations[user_id] = Conversation()
    
    conversation = user_conversations[user_id]
    conversation.add_message("user", message.text)
    
    try:
        # Получаем ответ от DeepSeek
        response = await deepseek.chat_complete(conversation.get_messages())
        conversation.add_message("assistant", response)
        
        # Разбиваем длинные сообщения на части
        max_length = 4096
        for i in range(0, len(response), max_length):
            await message.answer(response[i:i+max_length])
            
    except Exception as e:
        logger.error(f"Error in message handling: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())