from aiogram.utils import executor
from pyfiglet import Figlet
from dir_bot import create_bot
from dir_base import sqlite_db
from dir_bot import client

async def on_startup(_):
    preview_text = Figlet(font='slant')
    print(preview_text.renderText("BOT STOCKS"))
    sqlite_db.sql_start()


def main():
    executor.start_polling(create_bot.dp, skip_updates=True, on_startup=on_startup)


if __name__ == "__main__":
    main()
