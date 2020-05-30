import os
import requests as rq
import logging
import sentry_sdk
import time
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from dotenv import load_dotenv

sentry_sdk.init("https://112f0bcd65ad40ad938a287a0d4ff8b9@o335977.ingest.sentry.io/5250334")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

IS_HEROKU = os.environ.get('IS_HEROKU', False)
if IS_HEROKU:
    print('HEROKU IS  DETECTED ')
else:
    print('HEROKU IS NOT DETECTED. LOAD ENVIRONMENT FROM .ENV ')
    load_dotenv()

bot_token = os.environ.get('tg_token')
OWN_ID = os.environ.get('telegram_id')
ya_server_url = os.environ.get('homework_url')
homework_token = os.environ.get('homework_token')

bot = Bot(bot_token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply('Welcome to YANDEX Homework Status Information System!\n'
                        '/help - for command list. ')


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply('Task reporter Bot. Demo version 0.1 \n'
                        '/start command list \n'
                        '/last - get last task status.\n'
                        '/list - get all tasks\n'
                        '/active - show only uncompleted '
                        'home_works.\n'
                        '/track_on - set track on \n'
                        '/track_off - set track off \n')


if __name__ == '__main__':
    executor.start_polling(dp)
