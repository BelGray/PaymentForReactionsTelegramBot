from aiogram import Bot, Dispatcher, Router
from modules import bot_config_manager

config = bot_config_manager.BotConfig()
telegram = config.telegram_token
yoomoney = config.youmoney_token

bot = Bot(token=telegram)
dp = Dispatcher()
