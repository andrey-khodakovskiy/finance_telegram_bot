import logging
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from app.functions.connection_to_db import connection
from app.functions.functions import get_all_stats, get_player_stats


logger = logging.getLogger("common")
logger.setLevel(logging.INFO)
logfile = logging.FileHandler("logs/conversation.log")
logfile.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s", datefmt="%d-%b-%Y %H:%M:%S"
)
logfile.setFormatter(formatter)
logger.addHandler(logfile)


async def cmd_my_finance(message: types.Message, state: FSMContext) -> None:
    logger.info(
        f"'{message.text}' от {message.from_user.full_name} ({message.from_user.username} id: {message.from_user.id})"
    )
    await state.finish()
    user_telegram_id = message.from_user.id
    text = get_player_stats(connection, telegram_id=user_telegram_id)

    await message.answer(text)


async def cmd_all_finance(message: types.Message, state: FSMContext) -> None:
    logger.info(
        f"'{message.text}' от {message.from_user.full_name} ({message.from_user.username} id: {message.from_user.id})"
    )
    await state.finish()
    user_telegram_id = message.from_user.id
    text = get_all_stats(connection, user_telegram_id)

    await message.answer(text)


def register_handlers_common(dp: Dispatcher) -> None:
    dp.register_message_handler(cmd_my_finance, commands="my_finance", state="*")
    dp.register_message_handler(cmd_all_finance, commands="all_finance", state="*")
