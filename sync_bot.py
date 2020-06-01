import os
import requests as rq
import logging
import sentry_sdk
import time
import emoji
import asyncio
import aiohttp

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from datetime import timedelta
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
YA_SERVER_URL = os.environ.get('homework_url')
PRACTICUM_TOKEN = os.environ.get('homework_token')

bot = Bot(bot_token)
dp = Dispatcher(bot)

BOT_STATUS = {
    'active': True,
    'time_start': time.time(),
    'time_stop': None,
}


def get_formatted_data(server_list):
    task_str = ''
    if isinstance(server_list, dict):

        task_str += (
                server_list.get('homework_name') + '  ' + server_list.get('date_updated') + '  '
                + server_list.get('status'))
    else:
        for v in server_list:
            status = emoji.emojize(':v: ', use_aliases=True) if v.get('status') == 'approved' else \
                emoji.emojize(':x:', use_aliases=True)
            task_str += (v.get('homework_name') + '  ' + v.get('date_updated') + '  ' + status + '\n')
    return task_str


async def get_homework_statuses(current_timestamp):
    headers = {
        'Authorization': f'OAuth {PRACTICUM_TOKEN}',
    }
    params = {
        'from_date': current_timestamp
    }
    async with aiohttp.ClientSession() as session:
        response = await session.get(YA_SERVER_URL, params=params, headers=headers)
        assert response.status == 200
        return await response.json()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(emoji.emojize(':santa: ', use_aliases=True) + 'Welcome to YANDEX Homework '
                                                                      'Status Information System!\n'
                                                                      '/help - for command list. ')


@dp.message_handler(commands=['active'])
async def process_active_list(message: types.Message):
    task_list = []
    server_list = await get_homework_statuses(0)
    try:
        for task in server_list['homeworks']:
            if task.get('status') != 'approved':
                task_list.append(task)
    except KeyError as er:
        print(f'Key not found! Error : {er}')

    answer = get_formatted_data(task_list) if task_list else 'All homeworks are approved!'
    await bot.send_message(chat_id=OWN_ID, text=answer)


@dp.message_handler(commands=['list'])
async def process_list_command(message: types.Message):
    task_list = await get_homework_statuses(0)
    await bot.send_message(chat_id=OWN_ID, text=get_formatted_data(task_list.get('homeworks')))


@dp.message_handler(commands=['last'])
async def process_last_command(message: types.Message):
    task_list = await get_homework_statuses(0)
    last_job = task_list.get('homeworks')[0]
    await bot.send_message(chat_id=OWN_ID, text=get_formatted_data(last_job))


@dp.message_handler(commands=['track'])
async def process_track_command(message: types.Message):
    keyboard_markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    buttons_text = ('Active', 'Idle')
    keyboard_markup.row(*(types.KeyboardButton(text) for text in buttons_text))
    await message.reply('Do you want to set another status for server tracking?', reply_markup=keyboard_markup)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply('Task reporter Bot. Demo version 0.1 \n'
                        '/start command list \n'
                        '/last - get last task status.\n'
                        '/list - get all tasks\n'
                        '/active - show only uncompleted '
                        'home_works.\n'
                        '/track - set track on/off \n')


async def parse_homework_status(homework) -> str:
    await asyncio.sleep(0)
    homework_name = homework.get('homework_name')
    if homework.get('status') != 'approved':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


async def get_current_status() -> None:
    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        if not BOT_STATUS['active']:
            print(f'Bot idle for {str(timedelta(seconds=time.time() - BOT_STATUS["time_stop"]))}')
            await asyncio.sleep(60)
        else:
            try:
                logging.info('Getting request from server ...')
                new_homework = await get_homework_statuses(current_timestamp)
                if new_homework.get('homeworks'):
                    answer = await parse_homework_status(new_homework.get('homeworks')[0])
                    await bot.send_message(OWN_ID, answer)
                current_timestamp = new_homework.get('current_date')  # обновить timestamp
                logging.info('Sleeping for 300 sec. ')
                await asyncio.sleep(300)

            except asyncio.CancelledError as e:
                print(f'Bot has failed with : {e}')
                await asyncio.sleep(5)
                continue


@dp.message_handler()
async def all_msg_handler(message: types.Message):
    button_text = message.text

    if button_text == 'Active':
        try:
            BOT_STATUS['active'] = True
        except KeyError as er:
            print(f'Key Error ! {er}')
        reply_text = 'Bot status: Active.'
        BOT_STATUS['time_start'] = time.time()
        print(f'Tracking SET ON')
    elif button_text == 'Idle':
        try:
            BOT_STATUS['active'] = False
        except KeyError as er:
            print(f'Key Error ! {er}')
        reply_text = 'Bot status: Waiting.'
        BOT_STATUS['time_stop'] = time.time()
        print(f'Tracking SET OFF')
    else:
        reply_text = 'Keep previous state.'

    await message.reply(reply_text, reply_markup=types.ReplyKeyboardRemove())


async def main():
    await get_current_status()


if __name__ == '__main__':
    dp.loop.create_task(main())
    executor.start_polling(dp, skip_updates=True)

'''
def timer_start():
    threading.Timer(30.0, timer_start).start()
    try:
        asyncio.run_coroutine_threadsafe(save_data(),bot.loop)
    except Exception as exc:
        pass
'''
