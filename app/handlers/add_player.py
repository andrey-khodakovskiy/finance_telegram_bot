from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import logging
from typing import List, Set, Dict, Tuple, Union, Any

from app.functions.connection_to_db import connection
from app.functions.functions import add_user


logger = logging.getLogger("add_player")
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
    add_player = State()


async def cmd_add_player(message: types.Message, state: FSMContext) -> None:
    logger.info(
        f"'{message.text}' от {message.from_user.full_name} ({message.from_user.username} id: {message.from_user.id})"
    )
    await message.answer("Введите имя и фамилию:")
    await Admin.add_player.set()


async def add_player_get_message(message: types.Message, state: FSMContext) -> None:
    try:
        name, surname = message.text.split()
    except:
        await message.answer("Имя и фамилия введены неправильно. Попробуйте еще раз")
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text="Добавить", callback_data="add"),
        types.InlineKeyboardButton(text="Отмена", callback_data="exit"),
    ]
    markup.add(*buttons)

    await message.answer(f"Новый игрок:\n{name} {surname}", reply_markup=markup)
    await state.update_data(new_player=(name, surname))


async def add_player_get_callback_add(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    user_data = await state.get_data()
    name, surname = user_data["new_player"]
    result = add_user(connection, name, surname)

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text="Добавить еще", callback_data="add_another"),
        types.InlineKeyboardButton(text="Выход", callback_data="exit"),
    ]
    markup.add(*buttons)
    await call.message.edit_text(result, reply_markup=markup)
    logger.info(
        f"'{call.message.text}' от {call.message.from_user.full_name} ({call.message.from_user.username} id: {call.message.from_user.id})"
    )
    await state.reset_data()
    await call.answer()


async def add_player_get_callback_add_another(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    await call.answer()
    await call.message.edit_text(
        call.message.text
    )  # Removes inline buttons from previous message on restart
    await cmd_add_player(message=call.message, state=state)


def register_handlers_add_player(dp: Dispatcher) -> None:
    dp.register_message_handler(
        cmd_add_player, commands="add_player", state=Admin.waiting_for_selection
    )
    dp.register_message_handler(add_player_get_message, state=Admin.add_player)
    dp.register_callback_query_handler(
        add_player_get_callback_add, text="add", state=Admin.add_player
    )
    dp.register_callback_query_handler(
        add_player_get_callback_add_another, text="add_another", state=Admin.add_player
    )
