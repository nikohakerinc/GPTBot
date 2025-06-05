import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

import base64
import requests
from openai import OpenAI

from config import token
from config import key

TOKEN = token
dp = Dispatcher()
client = OpenAI(api_key=key)

def ask_gpt4o(text):
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': f'{text}'},
        ]
    )
    answer=response.choices[0].message.content
    print(answer)
    return(answer)

@dp.message()
async def telegram(message: Message) -> None:
    answer = ask_gpt4o(message.text)
    try:
        await message.answer(answer)
    except TypeError:
        await message.answer('Nice try!')

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())