from dotenv import load_dotenv
import os

from constants import errors

from aiogram import Bot

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
if TOKEN is None or not TOKEN:
    raise errors.BOT_TOKEN_IS_NONE

try:
    bot = Bot(token=TOKEN)
except Exception as e:
    print(e)
