from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import logging
from typing import List, Set, Dict, Tuple, Union, Any
from decouple import config, Csv

from app.functions.connection_to_db import connection
from app.functions.queries_data import months_rus

ADMINS = config("ADMINS", cast=Csv(int))


logger = logging.getLogger("admin")
logger.setLevel(logging.INFO)
logfile = logging.FileHandler("logs/conversation.log")
logfile.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s", datefmt="%d-%b-%Y %H:%M:%S"
)
logfile.setFormatter(formatter)
logger.addHandler(logfile)


class Admin(StatesGroup):
    waiting_for_selection = State()


async def cmd_start(message: types.Message, state: FSMContext) -> None:
    logger.info(
        f"'{message.text}' от {message.from_user.full_name} ({message.from_user.username} id: {message.from_user.id})"
    )
    await state.finish()
    if not message.from_user.id in ADMINS:
        await message.answer("Извините, данный функционал вам не доступен")
        return

    reply_keyboard = [["/add_player", "/del_player", "/exit"]]
    markup = types.ReplyKeyboardMarkup(
        reply_keyboard, resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer("Привет!", reply_markup=markup)

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text="Сезон", callback_data="season"),
        types.InlineKeyboardButton(text="Тренировки", callback_data="trainings"),
        types.InlineKeyboardButton(text="Оплата игры", callback_data="spending"),
        types.InlineKeyboardButton(text="Отчет", callback_data="report"),
    ]
    markup.add(*buttons)
    await message.answer("Внести данные:", reply_markup=markup)

    await Admin.waiting_for_selection.set()


async def cmd_exit(message: types.Message, state: FSMContext) -> None:
    await state.reset_data()
    await state.finish()
    await message.answer("/start", reply_markup=types.ReplyKeyboardRemove())


async def exit_get_callback(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await call.message.edit_text(
        call.message.text
    )  # Removes inline buttons from previous message on restart
    await cmd_exit(message=call.message, state=state)


def register_handlers_admin(dp: Dispatcher) -> None:
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_exit, commands="exit", state="*")
    dp.register_callback_query_handler(exit_get_callback, text="exit", state="*")
