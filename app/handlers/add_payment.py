from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import logging
from typing import List, Set, Dict, Tuple, Union, Any

from app.handlers.admin import cmd_exit
from app.functions.connection_to_db import connection
from app.functions.queries_data import months_rus
from app.functions.functions import (
    set_summ,
    get_all_players,
    get_player_stats,
    get_user_id_by_name,
    get_month,
    add_spending,
    create_report,
)


logger = logging.getLogger("add_payment")
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
    add_payment = State()
    add_spending = State()
    add_spending_description = State()


async def start_get_callback_season(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    payment_type = call.data
    await state.update_data(payment_type=payment_type)

    players = get_all_players(connection)
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(text=player[0], callback_data=player[0])
        for player in players
    ]
    markup.add(*buttons)

    await call.message.edit_text("Выберите игрока:", reply_markup=markup)
    await call.answer()
    await Admin.add_payment.set()


async def add_payment_get_callback_name(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    name, surname = call.data.split()
    await state.update_data(name=name, surname=surname)

    month_eng = get_month()
    month_rus = months_rus[month_eng]
    user_data = await state.get_data()
    payment_type_text = (
        "Сезон" if user_data["payment_type"] == "season" else f"Тренировки {month_rus}"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text="+1000", callback_data="1000"),
        types.InlineKeyboardButton(text="+2000", callback_data="2000"),
        types.InlineKeyboardButton(text="+3000", callback_data="3000"),
        types.InlineKeyboardButton(text="+5000", callback_data="5000"),
        types.InlineKeyboardButton(text="+500", callback_data="500"),
        types.InlineKeyboardButton(text="другая сумма", callback_data="other"),
    ]
    markup.add(*buttons)
    await call.message.edit_text(
        f"<b>{user_data['name']} {user_data['surname']}</b>\n{payment_type_text}:",
        reply_markup=markup,
    )
    await call.answer()


async def add_payment_get_callback_summ(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    summ = call.data
    await state.update_data(summ=summ)

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text="OK", callback_data="confirm"),
        types.InlineKeyboardButton(text="Отмена", callback_data="exit"),
    ]
    markup.add(*buttons)
    await call.message.edit_text(
        call.message.text + f" +{summ} руб.", reply_markup=markup
    )
    await call.answer()


async def add_payment_get_callback_summ_other(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    await call.message.edit_text(call.message.text)
    await call.message.answer("Введите сумму:")
    await call.answer()


async def add_payment_get_message_summ_other(
    message: types.Message, state: FSMContext
) -> None:
    try:
        summ = int(message.text)
    except:
        await message.answer("Сумма введена неверно. Попробуйте еще раз")
        return
    await state.update_data(summ=summ)

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text="OK", callback_data="confirm"),
        types.InlineKeyboardButton(text="Отмена", callback_data="exit"),
    ]
    markup.add(*buttons)

    user_data = await state.get_data()
    month_eng = get_month()
    month_rus = months_rus[month_eng]
    payment_type_text = (
        "Сезон" if user_data["payment_type"] == "season" else f"Тренировки {month_rus}"
    )
    await message.answer(
        f"<b>{user_data['name']} {user_data['surname']}</b>\n{payment_type_text}: +{user_data['summ']} руб.",
        reply_markup=markup,
    )


async def add_payment_get_callback_confirm(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    user_data = await state.get_data()
    set_summ(
        connection,
        user_data["name"],
        user_data["surname"],
        user_data["payment_type"],
        user_data["summ"],
    )
    cursor = connection.cursor()
    user_id = get_user_id_by_name(cursor, user_data["name"], user_data["surname"])[0]
    text = get_player_stats(connection, player_id=user_id)

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text="Внести еще", callback_data="another"),
        types.InlineKeyboardButton(text="Выход", callback_data="exit"),
    ]
    markup.add(*buttons)
    await call.message.edit_text("<u>Обновлено</u>\n" + text, reply_markup=markup)
    await call.answer()
    logger.info(
        f"'{user_data['name']} {user_data['surname']} {user_data['payment_type']} {user_data['summ']}' от {call.message.from_user.full_name} ({call.message.from_user.username} id: {call.message.from_user.id})"
    )


async def add_payment_get_callback_another(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    await call.answer()
    await call.message.edit_text(
        call.message.text
    )  # Removes inline buttons from previous message on restart

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text="Сезон", callback_data="season"),
        types.InlineKeyboardButton(text="Тренировки", callback_data="trainings"),
    ]
    markup.add(*buttons)
    await call.message.answer("Добавить взнос за:", reply_markup=markup)

    await Admin.waiting_for_selection.set()


async def start_get_callback_spending(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text="3600", callback_data="3600"),
        types.InlineKeyboardButton(text="другая сумма", callback_data="other"),
    ]
    markup.add(*buttons)

    await call.message.edit_text(
        "Оплата игры / квартальный взнос:", reply_markup=markup
    )
    await call.answer()
    await Admin.add_spending.set()


async def add_spending_get_callback_summ(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    summ = call.data
    await state.update_data(spending_summ=summ)

    await call.message.edit_text(f"Оплата игры {summ} руб.")
    await call.answer()
    await call.message.answer("Введите описание (например '31 тур')")
    await Admin.add_spending_description.set()


async def add_spending_get_callback_summ_other(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    await call.message.edit_text(call.message.text)
    await call.message.answer("Введите сумму:")
    await call.answer()


async def add_spending_get_message_summ_other(
    message: types.Message, state: FSMContext
) -> None:
    try:
        summ = int(message.text)
    except:
        await message.answer("Сумма введена неверно. Попробуйте еще раз")
        return
    await state.update_data(spending_summ=summ)

    await message.answer(f"Оплата {summ} руб.")
    await message.answer("Введите описание (например 'взнос за 1 квартал')")
    await Admin.add_spending_description.set()


async def add_spending_get_message_description(
    message: types.Message, state: FSMContext
) -> None:
    description = message.text
    await state.update_data(spending_description=description)
    user_data = await state.get_data()

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text="OK", callback_data="confirm"),
        types.InlineKeyboardButton(text="Отмена", callback_data="exit"),
    ]
    markup.add(*buttons)
    await message.answer(
        f"Оплата {user_data['spending_summ']} руб.\n{description}", reply_markup=markup
    )
    await Admin.add_spending.set()


async def add_spending_get_callback_confirm(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    logger.info(
        f"'{call.message.text}' от {call.message.from_user.full_name} ({call.message.from_user.username} id: {call.message.from_user.id})"
    )
    user_data = await state.get_data()
    add_spending(
        connection, user_data["spending_summ"], user_data["spending_description"]
    )
    await call.message.edit_text("Информация добавлена")
    await state.reset_data()
    await call.answer()

    last_spendings, report = create_report(connection)
    await call.message.answer("<u>Последние оплаты:</u>\n" + last_spendings)
    await call.message.answer(report)
    await cmd_exit(message=call.message, state=state)


async def start_get_callback_report(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    logger.info(
        f"'report' от {call.message.from_user.full_name} ({call.message.from_user.username} id: {call.message.from_user.id})"
    )
    last_spendings, report = create_report(connection)
    await call.answer()
    await call.message.edit_text("<u>Последние оплаты:</u>\n" + last_spendings)
    await call.message.answer(report)
    await cmd_exit(message=call.message, state=state)


def register_handlers_add_payment(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(
        start_get_callback_season,
        text=["season", "trainings"],
        state=Admin.waiting_for_selection,
    )
    dp.register_callback_query_handler(
        start_get_callback_spending,
        text="spending",
        state=Admin.waiting_for_selection,
    )
    dp.register_callback_query_handler(
        start_get_callback_report,
        text="report",
        state=Admin.waiting_for_selection,
    )
    dp.register_callback_query_handler(
        add_payment_get_callback_summ,
        text=["1000", "2000", "3000", "5000", "500"],
        state=Admin.add_payment,
    )
    dp.register_callback_query_handler(
        add_payment_get_callback_summ_other, text="other", state=Admin.add_payment
    )
    dp.register_message_handler(
        add_payment_get_message_summ_other,
        state=Admin.add_payment,
    )  # Handles other summ input
    dp.register_callback_query_handler(
        add_payment_get_callback_confirm,
        text="confirm",
        state=Admin.add_payment,
    )
    dp.register_callback_query_handler(
        add_payment_get_callback_another,
        text="another",
        state=Admin.add_payment,
    )
    dp.register_callback_query_handler(
        add_payment_get_callback_name, state=Admin.add_payment
    )  # Handles player name callback
    dp.register_callback_query_handler(
        add_spending_get_callback_summ,
        text="3600",
        state=Admin.add_spending,
    )
    dp.register_callback_query_handler(
        add_spending_get_callback_summ_other, text="other", state=Admin.add_spending
    )
    dp.register_callback_query_handler(
        add_spending_get_callback_confirm,
        text="confirm",
        state=Admin.add_spending,
    )
    dp.register_message_handler(
        add_spending_get_message_summ_other,
        state=Admin.add_spending,
    )  # Handles other summ input
    dp.register_message_handler(
        add_spending_get_message_description,
        state=Admin.add_spending_description,
    )
