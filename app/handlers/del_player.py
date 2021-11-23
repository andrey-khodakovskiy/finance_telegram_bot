from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import logging
from typing import List, Set, Dict, Tuple, Union, Any

from app.functions.connection_to_db import connection
from app.functions.functions import del_user, get_all_players


logger = logging.getLogger("del_player")
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
    del_player = State()


async def cmd_del_player(message: types.Message, state: FSMContext) -> None:
    logger.info(
        f"'{message.text}' от {message.from_user.full_name} ({message.from_user.username} id: {message.from_user.id})"
    )
    players = get_all_players(connection)
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(text=player[0], callback_data=player[0])
        for player in players
    ]
    markup.add(*buttons)

    await message.answer("Выберите игрока:", reply_markup=markup)
    await Admin.del_player.set()


async def del_player_get_callback_name(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    name, surname = call.data.split()
    await state.update_data(del_player=(name, surname))

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text="Удалить", callback_data="del"),
        types.InlineKeyboardButton(text="Отмена", callback_data="exit"),
    ]
    markup.add(*buttons)

    await call.message.edit_text(
        f"Удалить игрока?\n{name} {surname}", reply_markup=markup
    )
    await call.answer()


async def del_player_get_callback_del(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    user_data = await state.get_data()
    name, surname = user_data["del_player"]
    result = del_user(connection, name, surname)

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text="Удалить еще", callback_data="del_another"),
        types.InlineKeyboardButton(text="Выход", callback_data="exit"),
    ]
    markup.add(*buttons)
    await call.message.edit_text(result, reply_markup=markup)
    logger.info(
        f"'{call.message.text}' от {call.message.from_user.full_name} ({call.message.from_user.username} id: {call.message.from_user.id})"
    )
    await state.reset_data()
    await call.answer()


async def del_player_get_callback_del_another(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    await call.answer()
    await call.message.edit_text(
        call.message.text
    )  # Removes inline buttons from previous message on restart
    await cmd_del_player(message=call.message, state=state)


def register_handlers_del_player(dp: Dispatcher) -> None:
    dp.register_message_handler(
        cmd_del_player, commands="del_player", state=Admin.waiting_for_selection
    )
    dp.register_callback_query_handler(
        del_player_get_callback_del, text="del", state=Admin.del_player
    )
    dp.register_callback_query_handler(
        del_player_get_callback_del_another, text="del_another", state=Admin.del_player
    )
    dp.register_callback_query_handler(
        del_player_get_callback_name, state=Admin.del_player
    )
