from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import handlers.admin as admin_router
import handlers.user as user_router
import logging
import sys


from yamlparser import Telegram

dp = Dispatcher()
async def setup_handlers(dp: Dispatcher):
    dp.include_router(admin_router.prepare_router())
    dp.include_routers(
        admin_router.prepare_router(),
        user_router.prepare_router()
    )

async def start_bot(config):
    telegram_config = Telegram(config)
    bot = Bot(token=telegram_config.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    dp['bot_config'] = telegram_config
    await setup_handlers(dp)
    await dp.start_polling(bot)

