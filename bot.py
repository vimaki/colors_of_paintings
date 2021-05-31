#!/usr/bin/python

"""Telegram bot for extracting the primary colors from an image.

An asynchronous telegram bot using the AIOgram library. The bot takes
an image from the user, the number of colors required utilizing
the keyboard, and returns the resulting infographic.

Functions
---------
interface_description
    Display of help information.
bot_description
    Displays a welcome explanatory message.
user_image
    Receiving a photo from a user.
another_number_of_colors
    Use a previously uploaded photo.
set_colors_number
    Selects the number of colors to extract from the image.
get_result_image
    Loading the resulting infographic.
on_startup
    Start webhook.
on_shutdown
    Finish webhook.

References
----------
async_business_logic_call.py
    A module is containing asynchronous access to the web application's
    business logic.
"""

import logging
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.types.input_file import InputFile
from aiogram.utils.executor import start_webhook
from dotenv import load_dotenv

import async_business_logic_call

logging.basicConfig(level=logging.INFO)

# dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# if os.path.exists(dotenv_path):
#     load_dotenv(dotenv_path)
# else:
#     logging.warning('Invalid environment variables!')
#     sys.exit(1)

BOT_TOKEN = os.getenv('BOT_TOKEN')

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT'))

bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


# States of the finite state machine
class BusinessLogic(StatesGroup):
    picture = State()
    colors = State()


@dp.message_handler(commands=['help'])
async def interface_description(message: types.Message):
    """Display of help information."""
    await bot.send_message(chat_id=message.from_user.id, text='''
First, upload an image.
    
Then select the number of extracted colors using the buttons.
    
After these steps, you'll get the resulting infographic.

Use the command '/same' to assign a different number of extracted colors to the last loaded picture.

Use the command '/help' to show this help information.
    ''')


@dp.message_handler(commands=['start', 'help'])
async def bot_description(message: types.Message):
    """Displays a welcome explanatory message."""
    await bot.send_message(
        chat_id=message.from_user.id,
        text='*This bot extracts several averaged primary colors that dominate the image.*',
        parse_mode='Markdown'
    )
    await interface_description(message=message)


@dp.message_handler(content_types=['photo'])
async def user_image(message: types.Message):
    """Receiving a photo from a user."""
    await message.photo[-1].download(f'images/input_{message.from_user.id}.jpg')
    await BusinessLogic.picture.set()
    await set_colors_number(message=message,
                            state=Dispatcher.get_current().current_state())


@dp.message_handler(commands=['same'])
async def another_number_of_colors(message: types.Message):
    """Use a previously uploaded photo."""
    await BusinessLogic.picture.set()
    await set_colors_number(message=message,
                            state=Dispatcher.get_current().current_state())


# Keyboard for selecting the number of colors to extract.
keyboard_colors_number = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(f'{i}') for i in range(1, 11)],
        [KeyboardButton(f'{i}') for i in range(11, 21)]
    ],
    resize_keyboard=True
)


@dp.message_handler(state=BusinessLogic.picture)
async def set_colors_number(message: types.Message, state: FSMContext):
    """Selects the number of colors to extract from the image."""
    await BusinessLogic.next()
    await bot.send_message(
        chat_id=message.from_user.id,
        text='Choose the number of colors',
        reply_markup=keyboard_colors_number
    )


@dp.message_handler(state=BusinessLogic.colors)
async def get_result_image(message: types.Message, state: FSMContext):
    """Loading the resulting infographic."""
    await message.answer('Please wait until calculations are finished',
                         reply_markup=ReplyKeyboardRemove())

    image_path = f'images/input_{message.from_user.id}.jpg'
    output_image_path = f'images/output_{message.from_user.id}.jpg'
    number_of_colors = int(message.text)
    await async_business_logic_call.async_get_colors(
        image=image_path,
        number_of_colors=number_of_colors,
        create_image=True,
        output_image_path=output_image_path
    )

    output_image = InputFile(output_image_path)
    await bot.send_photo(message.from_user.id, output_image)
    await state.finish()


async def on_startup(dp):
    """Start webhook."""
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp):
    """Finish webhook."""
    logging.warning('Shutting down..')

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
