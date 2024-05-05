import asyncio
from aiogram.filters.command import Command
from bot.loader import dp, bot



async def on_ready():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(on_ready())