import asyncio

import logging
from decouple import config

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.handlers.common import register_handlers_common
from app.handlers.admin import register_handlers_admin
from app.handlers.add_player import register_handlers_add_player
from app.handlers.del_player import register_handlers_del_player
from app.handlers.add_payment import register_handlers_add_payment
from app.functions.create_tables import create_tables
from app.functions.connection_to_db import connection


logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.WARNING)

BOT_TOKEN = config("BOT_TOKEN")


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/my_finance", description="Информация о моих взносах"),
        BotCommand(command="/all_finance", description="Общая таблица"),
    ]
    await bot.set_my_commands(commands)


async def main():

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[console],
    )
    logger.error("Starting bot")

    create_tables(connection)

    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_handlers_common(dp)
    register_handlers_admin(dp)
    register_handlers_add_player(dp)
    register_handlers_del_player(dp)
    register_handlers_add_payment(dp)

    await set_commands(bot)
    await dp.skip_updates()
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
