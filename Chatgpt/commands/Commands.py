import sys

from aiogram import Bot, types
from dispatcher.Dispatcher import bot
from dispatcher.Dispatcher import dp


async def set_commands():
    commands = [
        types.BotCommand("start", "🔁Перезапуск бота"),
        types.BotCommand("profile", "👤Мой профиль"),
        types.BotCommand("premium", "🚀Премиум подписка"),
        types.BotCommand("personality", "🎭Выбор роли"),
        types.BotCommand("deletecontext", "❌Удалить контекст"),
        types.BotCommand("gptprompts", "📗Руководство для ChatGPT"),
        types.BotCommand("dalleprompts", "📘Руководство для DALL-E"),
        types.BotCommand("settings", "⚙️Настройки"),
        types.BotCommand("img", "🏙Сгенерировать картинку"),
        types.BotCommand("info", "ℹ️Возможности и команды"),
        types.BotCommand("help", "❓Помощь"),
        types.BotCommand("terms", "📜Условия пользования")
    ]
    await bot.set_my_commands(commands)


async def on_startup(dp):
    await set_commands()

