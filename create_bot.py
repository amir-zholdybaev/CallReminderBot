from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())

CHAT_ID = int(os.getenv('CHAT_ID'))
OWNER_ID = int(os.getenv('OWNER_ID'))
BOT_NAME = os.getenv('BOT_NAME')
POSTGRES_USER_PASSWORD = os.getenv('POSTGRES_USER_PASSWORD')


def main():
    pass


if __name__ == '__main__':
    main()
