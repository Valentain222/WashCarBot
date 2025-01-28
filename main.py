from aiogram import Dispatcher
import asyncio

from bot_setup import bot

from router_setup import router

dp = Dispatcher()
dp.include_router(router)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
