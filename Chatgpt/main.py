import threading
import datetime
import aiohttp
import asyncio
import aiogram
import logging
import time
import json
import pytz
import io
import os

from io import BytesIO
from PIL import Image
from config.Config import TG_BOT_TOKEN
from config.Config import CHANNEL_ID
from config.Config import SERVER_CRT, SERVER_KEY
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import hlink
from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram.types import InputMediaAudio
from aiogram.types import CallbackQuery
from aiogram.types import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.message import ContentType
from commands.Commands import on_startup
from markups.Markups import *
from dispatcher.Dispatcher import dp
from dispatcher.Dispatcher import bot
from handlers.Handlers import *
from datetime import timedelta
from database.db import db


logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    username = message.from_user.first_name
    if await check_subscription(CHANNEL_ID, message.chat.id):
        user_id = message.chat.id
        if not await db.user_exists(user_id):
            await db.add_user(user_id)
        await db.delete_history(user_id)
        await bot.send_message(message.chat.id, """Привет! 🤖👋

Наш бот предоставляет доступ к ChatGPT 3.5, ChatGPT 4 и DALL-E 3 для создания текстов и изображений.

Мы используем последние модели: GPT-4 Turbo, DALL-E 3, а также предыдущие версии GPT-4 и GPT 3.5 Turbo.

Здесь вы можете выполнять самые разнообразные задачи:

📝 Создание и изменение текстов.
💻 Написание и редактирование кода.
🌐 Перевод с любого языка.
🧠 Анализ и краткое изложение неструктурированного текста.
💬 Дружелюбный разговор и поддержка.
🎨 Создание графики по текстовым описаниям.
🌍 Быстрый поиск нужной информации.

<b>✉️ Чтобы получить ответ, напишите свой вопрос в чат (выберите модель GPT в /settings).</b>

<b>🤖 Доступные команды  - /info</b>
<b>🔐🤖Дополнительные фунции бота + гайд по пользованию - /help</b>

<b>📷 Для генерации картинки введите команду /img и ваш запрос.</b>
  Пример: /img Белый пушистый кот.
   Если вы отправите боту фотографию, он может ее отредактировать, переделать в аниме, распознать текст, решить задание, ответить на ваш запрос по фото. 

❕Если бот вам не отвечает, перезапустите командой /start

Удачи! 🚀✨""", parse_mode="HTML", reply_markup=await main_kb(), disable_web_page_preview=True)
    else:
        await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())


@dp.message_handler(commands=['help'])
async def command_help(message: types.Message):
    username = message.from_user.first_name
    if await check_subscription(CHANNEL_ID, message.chat.id):
        await bot.send_message(message.chat.id, """<b>📝 Генерация текстов</b>
Для генерации текстов напишите запрос в чат или отправьте голосовое сообщение. Пользователи с подпиской /premium могут получать голосовые ответы.

<b>/settings</b> – настройки бота и выбор модели GPT
<b>/GPTprompts</b> – руководство по написанию промптов для GPT
<b>/faq</b> – часто задаваемые вопросы по GPT и боту
<b>/help</b> - помощь

↩️ Если вы сделаете репост сообщений в бота с других каналов/чатов — он сможет озвучить их, изложить суть, переписать, написать статьи на их основе, изложить тезисно, либо выполнить Ваше индивидуальное задание.

<b>💬 Поддержка контекста</b>
По умолчанию бот запоминает контекст. Т.е. при подготовке ответа учитывает не только ваш текущий запрос, но и свой предыдущий ответ. Это позволяет вести диалог и задавать уточняющие вопросы. Чтобы начать диалог без учета предыдущего контекста, используйте команду /deletecontext. Контекст можно выключить в меню настроек командой /settings

👨‍👨‍👧‍👦 Бота можно добавить в группы (доступно на тарифах  🚀 Premium и выше). Чтобы задать ему вопрос в группе, используйте команду /ask "ваш запрос" (например, "/ask расскажи интересные факты о космосе").


<b>🌅 Генерация изображений</b>
Для генерации изображений в боте используются последние версии нейросетей Midjourney, Stable Diffusion и DALL-E. Доступны пользователям с подпиской /premium или в рамках отдельного пакета.

<b>/img</b> + <b>краткое описание</b> –  генерация изображения с помощью Midjourney, Stable Diffusion и DALL-E 3
<b>/Midjourney</b> – описание основного функционала генерации изображений с помощь Midjourney
<b>/StableDiffusion</b> — описание основного функционала генерации изображений с помощь Stable Diffusion
<b>/Dalle</b> — описание основного функционала генерации изображений с помощь DALL-E
<b>/midprompts</b> – описание расширенного функционала Midjourney с примерами: как использовать собственные изображения, менять версии, задавать параметры и др.
<b>/sdprompts</b> - описание расширенного функционала Stable Diffusion с примерами: как использовать собственные изображения, менять версии, задавать параметры и др.
<b>/Dalleprompts</b> - описание расширенного функционала DALL-E с примерами: как использовать собственные изображения, менять версии, задавать параметры и др.

📷 Если вы отправите боту фотографию, он может ее отредактировать, переделать в аниме, распознать текст, решить задание, ответить на Ваш запрос по фото. Вы также можете отправить фото боту и в подписи к нему указать свой вопрос или задание — запрос обработает GPT-4 Vision.

<b>⚙️ Другие команды</b>
<b>/start</b> - описание и перезапуск бота
<b>/profile</b> – ваш профиль, запросы  и баланс
<b>/premium</b> – подключение премиум подписки GPT, DALL-E , Midjourney, Stable Diffusion

""", parse_mode="HTML", reply_to_message_id=message.message_id)
    else:
        await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())


@dp.message_handler(commands=['info'])
async def command_info(message: types.Message):
    username = message.from_user.first_name
    if await check_subscription(CHANNEL_ID, message.chat.id):
         await bot.send_message(message.chat.id, """
Привет! 🤖👋

Наш бот предоставляет доступ к ChatGPT 3.5, ChatGPT 4 и DALL-E 3 для создания текстов и изображений.

Мы используем последние модели: GPT-4 Turbo, DALL-E 3, а также предыдущие версии GPT-4 и GPT 3.5 Turbo.

Здесь вы можете выполнять самые разнообразные задачи:

📝 Создание и изменение текстов.
💻 Написание и редактирование кода.
🌐 Перевод с любого языка.
🧠 Анализ и краткое изложение неструктурированного текста.
💬 Дружелюбный разговор и поддержка.
🎨 Создание графики по текстовым описаниям.
🌍 Быстрый поиск нужной информации.

✉️ Чтобы получить ответ, напишите свой вопрос в чат (выберите модель GPT в /settings).

🤖 Доступные команды:

/start — <i>Перезапустить бота</i>
/profile — <i>Мой профиль</i>
/premium — <i>Приобрести подписку</i>
/personality — <i>Выбрать роль GPT</i>
/deletecontext — <i>Обнулить контекст беседы</i>
/gptprompts – <i>руководство по написанию промптов для</i> <b>GPT</b>
/dalleprompts - <i>руководство по написанию промтов для</i> <b>DALL-E</b>
/settings — <i>Настройки</i>
/img (описание) — <i>Сгенерировать картинку по описанию (пример: /img дом возле моря)</i>
/info — <i>Возможности и команды</i>
/help — <i>Помощь</i>
/terms - <i>Условия использования</i>

📷 Если вы отправите боту фотографию, он может ее отредактировать, переделать в аниме, распознать текст, решить задание, ответить на ваш запрос по фото.

👨‍👨‍👧‍👦 Бот работает в группах (доступно на тарифе Premium). Чтобы задать ему вопрос в группе, используйте команду /ask "ваш запрос" (например, "/ask расскажи интересные факты о космосе").

❕Если бот вам не отвечает, перезапустите командой /start

Удачи! 🚀✨""", parse_mode="HTML", disable_web_page_preview=True)
    else:
        await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())


@dp.message_handler(commands=['settings'])
async def command_voice(message: types.Message):
    user_id = message.chat.id
    username = message.from_user.first_name
    if await check_subscription(CHANNEL_ID, message.chat.id):
        db_context = await db.get_user_info(user_id, "context")
        db_voice = await db.get_user_info(user_id, "voice")
        db_context = db_context[0]
        db_voice = db_voice[0]
        await bot.send_message(message.chat.id, """В этом разделе вы можете изменить настройки:

1. Выбрать модель <b>GPT</b>
2. Выбрать роль для <b>ChatGPT</b>
3. Включить или отключить поддержку контекста. Когда контекст включен, бот учитывает свой предыдущий ответ для ведения диалога
4. Настроить голосовые ответы и выбрать голос <b>GPT</b>
(доступен в /premium)
""", parse_mode="HTML", reply_markup=await settings(db_context, db_voice))
    else:
        await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())

@dp.message_handler(commands=['deletecontext'])
async def process_delete_context(message: types.Message):
    username = message.from_user.first_name
    if await check_subscription(CHANNEL_ID, message.chat.id):
        user_id = message.chat.id
        await db.delete_history(user_id)
        await bot.send_message(message.chat.id, """<b>✅ Ваш диалог сброшен</b>""", parse_mode="HTML")
    else:
        await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())

@dp.message_handler(commands=['terms'])
async def command_profile(message: types.Message):
    username = message.from_user.first_name
    if await check_subscription(CHANNEL_ID, message.chat.id):
        textOffer =
        textСonfidentiality =
        await bot.send_message(message.chat.id, f"1. {textOffer}\n\n2. {textСonfidentiality}", parse_mode="Markdown", disable_web_page_preview=True)
    else:
        await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())

@dp.message_handler(commands=['gptprompts'])
async def command_profile(message: types.Message):
    username = message.from_user.first_name
    if await check_subscription(CHANNEL_ID, message.chat.id):
        textGPTtutorial =
        await bot.send_message(message.chat.id, textGPTtutorial, parse_mode="Markdown")
    else:
        await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())

@dp.message_handler(commands=['dalleprompts'])
async def command_profile(message: types.Message):
    username = message.from_user.first_name
    if await check_subscription(CHANNEL_ID, message.chat.id):
        textDALLEtutorial =
        await bot.send_message(message.chat.id, textDALLEtutorial, parse_mode="Markdown")
    else:
        await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())


role_disc = {
"default": "<b>Обычный 🔁</b> - это обычный пользователь, который использует чат GPT для общения и получения информации",
"add": "<b>Рекламный Эксперт 📣</b> - это человек, который использует чат GPT для продвижения товаров и услуг с помощью рекламных сообщений.",
"hack": "<b>Хакутый GPT 👁‍🗨</b> - это специалист по чат GPT, который постоянно ищет новые способы использования и расширения его функционала.",
"seo": "<b>CEO специалист 👔</b> - это бизнес-эксперт, который использует чат GPT для управления своей компанией и развития бизнес-стратегии.",
"psicho": "<b>Психолог 🧘‍♀</b>️ - это специалист по психологии, который использует чат GPT для консультирования и помощи людям в решении их проблем.",
"fullstack": "<b>Fullstack Разработчик 💻</b> - это специалист по разработке программного обеспечения, который использует чат GPT для создания и улучшения различных инструментов.",
"codegen": "<b>Генератор Кода 💡</b> - это чат GPT, который может генерировать коды для различных задач программирования.",
"tech": "<b>Технический Справочник 📚</b> - это чат GPT, который содержит информацию о технических терминах и процессах, а также может помогать в решении технических проблем.",
"repeater": "<b>Репетитор 🎓</b> - это специалист, который использует чат GPT для обучения и поддержки студентов и      школьников в различных предметах и навыках.",
"news": "<b>Новостной Агрегатор 🌐</b> - это чат GPT, который собирает и предоставляет пользователю последние новости и события из различных источников.",
"textred": "<b>Редактор Текста 📝</b> - это чат GPT, который может помогать пользователям с правописанием, грамматикой и стилем письма.",
"creative": "<b>Писатель Креативных Статей ✍</b>️ - это чат GPT, который помогает пользователям создавать оригинальный и увлекательный контент для блогов, сайтов и других публикаций.",
"finance": "<b>Финансовый Консультант 💰</b> - это чат GPT, который может давать советы и рекомендации по финансовым вопросам, таким как инвестиции, планирование бюджета и т.д.",
"twowords": "<b>Кратко ⏩</b> - это чат GPT, который может дать краткую информацию или описание по любой теме или запросу.",
}


@dp.message_handler(commands=['personality'])
async def command_personality(message: types.Message):
    username = message.from_user.first_name
    if await check_subscription(CHANNEL_ID, message.chat.id):
        user_id = message.chat.id
        role = await db.get_user_info(user_id, "role_preview")
        role = role[0]
        if role in role_disc:
            text_role = role_disc[role]
            await bot.send_message(message.chat.id, f"""<b>👤 Выберите роль для GPT:</b>\n\n{text_role}""", parse_mode="HTML", reply_to_message_id=message.message_id, reply_markup=await roles(None, role, None))
    else:
        await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())


role_for_profile = {
        "default": "Обычный 🔁",
        "add": "Рекламный Эксперт 📣",
        "hack": "Хакнутый GPT 👁‍🗨",
        "seo": "CEO специалист 👔",
        "psicho": "Психолог 🧘‍",
        "fullstack": "Fullstack Разраб-ик 💻",
        "codegen": "Генератор Кода 💡",
        "tech": "Техн-ий Справочник 📚",
        "repeater": "Репетитор 🎓",
        "news": "Новостной Агрегатор 🌐",
        "textred": "Редактор Текста 📝",
        "creative": "Писатель Статей ✍️",
        "finance": "Финан-ый Консультант 💰",
        "twowords": "Кратко ⏩",
    }

sub_for_profile = {
        "free": "🆓 Free",
        "mini": "👁‍🗨 Mini",
        "starter": "👌 Starter",
        "premium": "🚀 Premium",
        "ultra": "🔥 Ultra",
        "maximum": "💯 MAXIMUM",
    }


@dp.message_handler(commands=['profile'])
async def command_profile(message: types.Message):
    username = message.from_user.first_name
    if await check_subscription(CHANNEL_ID, message.chat.id):
        user_id = message.chat.id
        await check_user_sub(user_id)
        request_gpt_3 = await db.get_user_info(user_id, "request_gpt_3")
        request_gpt_4 = await db.get_user_info(user_id, "request_gpt_4")
        request_dalle = await db.get_user_info(user_id, "request_dalle")
        selected_model = await db.get_user_info(user_id, "selected_model")
        user_sub = time_sub_day(await db.get_time(user_id, "sub_time"))
        role = await db.get_user_info(user_id, "role_preview")
        context = await db.get_user_info(user_id, "context")
        voice = await db.get_user_info(user_id, "voice")
        sub = await db.get_user_info(user_id, "sub")
        selected_model = selected_model[0]
        request_gpt_3 = request_gpt_3[0]
        request_gpt_4 = request_gpt_4[0]
        request_dalle = request_dalle[0]
        context = context[0]
        voice = voice[0]
        role = role[0]
        sub = sub[0]

        moscow_tz = pytz.timezone('Europe/Moscow')
        now = datetime.datetime.now(moscow_tz)
        next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        time_difference = next_midnight - now
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        if user_sub == False:
            user_sub = "-"
        if request_gpt_3 < 0:
            request_gpt_3 = "∞"
        if request_gpt_4 < 0:
            request_gpt_4 = "∞"
        if request_dalle < 0:
            request_dalle = "∞"
        if context == "on":
            context = "✅ Вкл"
        elif context == "off":
            context = "❌ Выкл"
        if voice == "on":
            voice = "✅ Вкл"
        elif voice == "off":
            voice = "❌ Выкл"
        if sub in sub_for_profile:
            sub = sub_for_profile[sub]
        if role in role_for_profile:
            role = role_for_profile[role]

        await bot.send_message(message.chat.id, f"""<b>👨‍💻 Добро пожаловать!</b>
<b>├ Ваш ID:</b> {message.from_user.id}
<b>├ 💳 Подписка:</b> <b>{sub}</b>
<b>├ 🤖 Нейросеть:</b> {selected_model}
<b>├ 📆 Действует до:</b> {user_sub}
<b>├ 💭 GPT 3.5 запросы (24 ч):</b> {request_gpt_3}
<b>├ 💭 GPT 4.0 запросы (24 ч):</b> {request_gpt_4}
<b>├ 🖼 ️Картинок осталось (24 ч):</b> {request_dalle}
<b>├ 🎭 GPT-Роль:</b> {role}
<b>├ 📝 Контекст:</b> {context}
<b>├ 🔉 Голосовой ответ:</b> {voice}

<i>Лимит обновится через: {hours} ч. {minutes} мин.</i>

<b>🚀 Нужно больше?</b>
Переходи на одну из трех премиальных подписок командой /premium и открой новые возможности чат-бота с увеличенными лимитами""", parse_mode="HTML")
    else:
        await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())


@dp.message_handler(commands=['premium'])
async def command_premium(message: types.Message):
    username = message.from_user.first_name
    if await check_subscription(CHANNEL_ID, message.chat.id):
        await bot.send_message(message.chat.id, """🤖 Бот предлагает бесплатный дневной лимит в 20 запросов (GPT 3.5) на создание текста и 1 запрос в день на работу с вашими изображениями для обеспечения оптимальной скорости и качества.

💠 Нужно больше запросов и более мощная и продвинутая версия бота <b>GPT-4</b> и <b>GPT-4 Turbo</b>? Тогда выберите одну из следующих доступных подписок, включающих дополнительную функциональность и расширенные лимиты, либо приобретите запросы отдельно:

👁‍🗨 <b>Mini</b>
— GPT 3.5 — 100 сообщений в день
— GPT 4 — 10 сообщения в день
— 5 изображений в день
— Нейросеть Dalle для генерации высококачественных изображений
— Отсутствует пауза между запросами
— Решение задач по фото
— Создание аниме по фото
— Отсутствует реклама

👌 <b>Starter:</b>
— GPT 3.5 — безлимитно
— GPT 4 — 30 сообщений в день
— 25 изображений в день
— 9 моделей GPT, включая GPT 4 Turbo
— Зрение GPT 4 Vision
— Решение задач по фото
— Нейросети /Midjourney, /StableDiffusion и Dalle  для генерации высококачественных изображений
— Редактор изображений на основе ИИ
— Создание аниме по фотографии
— Возможность выбрать GPT личность для бота
— Увеличенный х2 контекст и длина ответа бота
— Отсутствует реклама

🚀 <b>Premium:</b>
— GPT 3.5 — безлимитно
— GPT 4 — 50 сообщений в день
— 50 изображений в день
— 9 моделей GPT, включая GPT 4 Turbo
— Зрение GPT 4 Vision
— Работает в группах Telegram
— Создание аниме по фотографии
— Нейросети /Midjourney, /StableDiffusion и Dalle 3 для генерации высококачественных изображений
— Редактор изображений на основе ИИ
— Компьютерное зрение: распознование текста с фото, решение любых задач и экзаменационных билетов, любые запросы по тексту на фото.
— Голосовое управление, распознавание голосовых сообщений и режим ответа голосом
— Возможность выбрать GPT личность для бота
— Помнит больше сообщений в истории чата для более качественного ответа
— Увеличенный х3 контекст и длина ответа бота
— отсутствует реклама

🔥 <b>Ultra:</b>
— GPT 3.5 — безлимитно
— GPT 4 — 100 сообщений в день
— 100 изображений в день
— 9 моделей GPT, включая GPT 4 Turbo
— Зрение GPT 4 Vision
— Работает в группах Telegram
— Нейросети /Midjourney, /StableDiffusion и Dalle 3 для генерации высококачественных изображений
— Возможность выбрать GPT личность для бота
— Возможность задать боту свою кастомную инструкцию
— Увеличенный х4 контекст и длина ответа бота
— Подключение бота к глобальной сети Интернет и использование полученной информации в своих ответах
— Доступ к бета версиям новых продуктов/нейросетей
— Все возможности Premium плана
— Отсутствует реклама

💯 <b>MAXIMUM</b>
— Безлимитный запросы на все функции.
— Вся функциональность бота доступна без ограничений.
— Работает в любых группах Telegram
— Отсутствует реклама
— Все функции прошлых подписок

<i>Функции /Midjourney, /StableDiffusion, /ask, GPT 4 Vision,  редакция изображений в настоящее время недоступны.</i>""", parse_mode="HTML", reply_markup=await create_premium_buttons("monthly", "мес", 400, 700, 1200, 1700, 3900, "monthly"))
    else:
        await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())


@dp.message_handler(regexp="👤Мой профиль")
async def process_profile(message: types.Message):
    username = message.from_user.first_name
    if await check_subscription(CHANNEL_ID, message.chat.id):
        moscow_tz = pytz.timezone('Europe/Moscow')
        now = datetime.datetime.now(moscow_tz)
        next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        time_difference = next_midnight - now
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        user_id = message.chat.id
        await check_user_sub(user_id)
        request_gpt_3 = await db.get_user_info(user_id, "request_gpt_3")
        request_gpt_4 = await db.get_user_info(user_id, "request_gpt_4")
        request_dalle = await db.get_user_info(user_id, "request_dalle")
        role = await db.get_user_info(user_id, "role_preview")
        voice = await db.get_user_info(user_id, "voice")
        context = await db.get_user_info(user_id, "context")
        selected_model = await db.get_user_info(user_id, "selected_model")
        sub = await db.get_user_info(user_id, "sub")
        sub = sub[0]
        user_sub = time_sub_day(await db.get_time(user_id, "sub_time"))
        if user_sub == None:
            user_sub = "-"
        request_gpt_3 = request_gpt_3[0]
        request_gpt_4 = request_gpt_4[0]
        request_dalle = request_dalle[0]
        if request_gpt_3 < 0:
            request_gpt_3 = "∞"
        if request_gpt_4 < 0:
            request_gpt_4 = "∞"
        if request_dalle < 0:
            request_dalle = "∞"
        context = context[0]
        if context == "on":
            context = "✅ Вкл"
        elif context == "off":
            context = "❌ Выкл"
        voice = voice[0]
        if voice == "on":
            voice = "✅ Вкл"
        elif voice == "off":
            voice = "❌ Выкл"
        role = role[0]
        if sub in sub_for_profile:
            sub = sub_for_profile[sub]
        if role in role_for_profile:
            role = role_for_profile[role]
        await bot.send_message(message.chat.id, f"""<b>👨‍💻 Добро пожаловать!</b>
<b>├ Ваш ID:</b> {message.from_user.id}
<b>├ 💳 Подписка:</b> <b>{sub}</b>
<b>├ 🤖 Нейросеть:</b> {selected_model[0]}
<b>├ 📆 Действует до:</b> {user_sub}
<b>├ 💭 GPT 3.5 запросы (24 ч):</b> {request_gpt_3}
<b>├ 💭 GPT 4.0 запросы (24 ч):</b> {request_gpt_4}
<b>├ 🖼 ️Картинок осталось (24 ч):</b> {request_dalle}
<b>├ 🎭 GPT-Роль:</b> {role}
<b>├ 📝 Контекст:</b> {context}
<b>├ 🔉 Голосовой ответ:</b> {voice}

<i>Лимит обновится через: {hours} ч. {minutes} мин.</i>

<b>🚀 Нужно больше?</b>
Переходи на одну из трех премиальных подписок командой /premium и открой новые возможности чат-бота с увеличенными лимитами""", parse_mode="HTML")
    else:
        await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())


@dp.message_handler(regexp="🎭GPT - Роли")
async def process_role(message: types.Message):
    username = message.from_user.first_name
    if await check_subscription(CHANNEL_ID, message.chat.id):
        user_id = message.chat.id
        role = await db.get_user_info(user_id, "role_preview")
        role = role[0]
        if role in role_disc:
            text_role = role_disc[role]
            await bot.send_message(message.chat.id, f"""<b>👤 Выберите роль для GPT:</b>\n\n{text_role}""", parse_mode="HTML", reply_markup=await roles(None, role, None))
    else:
        await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())


@dp.message_handler(regexp="🚀Премиум подписка")
async def process_premium(message: types.Message):
    username = message.from_user.first_name
    if await check_subscription(CHANNEL_ID, message.chat.id):
        await bot.send_message(message.chat.id, """🤖 Бот предлагает бесплатный дневной лимит в 20 запросов (GPT 3.5) на создание текста и 1 запрос в день на работу с вашими изображениями для обеспечения оптимальной скорости и качества.

💠 Нужно больше запросов и более мощная и продвинутая версия бота <b>GPT-4</b> и <b>GPT-4 Turbo</b>? Тогда выберите одну из следующих доступных подписок, включающих дополнительную функциональность и расширенные лимиты, либо приобретите запросы отдельно:

👁‍🗨 <b>Mini</b>
— GPT 3.5 — 100 сообщений в день
— GPT 4 — 10 сообщения в день
— 5 изображений в день
— Нейросеть Dalle для генерации высококачественных изображений
— Отсутствует пауза между запросами
— Решение задач по фото
— Создание аниме по фото
— Отсутствует реклама

👌 <b>Starter:</b>
— GPT 3.5 — безлимитно
— GPT 4 — 30 сообщений в день
— 25 изображений в день
— 9 моделей GPT, включая GPT 4 Turbo
— Зрение GPT 4 Vision
— Решение задач по фото
— Нейросети /Midjourney, /StableDiffusion и Dalle  для генерации высококачественных изображений
— Редактор изображений на основе ИИ
— Создание аниме по фотографии
— Возможность выбрать GPT личность для бота (15 видов)
— Увеличенный х2 контекст и длина ответа бота
— Отсутствует реклама

🚀 <b>Premium:</b>
— GPT 3.5 — безлимитно
— GPT 4 — 50 сообщений в день
— 50 изображений в день
— 9 моделей GPT, включая GPT 4 Turbo
— Зрение GPT 4 Vision
— Работает в группах Telegram
— Создание аниме по фотографии
— Нейросети /Midjourney, /StableDiffusion и Dalle 3 для генерации высококачественных изображений
— Редактор изображений на основе ИИ
— Компьютерное зрение: распознование текста с фото, решение любых задач и экзаменационных билетов, любые запросы по тексту на фото.
— Голосовое управление, распознавание голосовых сообщений и режим ответа голосом
— Возможность выбрать GPT личность для бота (50 видов)
— Помнит больше сообщений в истории чата для более качественного ответа
— Увеличенный х3 контекст и длина ответа бота
— отсутствует реклама

🔥 <b>Ultra:</b>
— GPT 3.5 — безлимитно
— GPT 4 — 100 сообщений в день
— 100 изображений в день
— 9 моделей GPT, включая GPT 4 Turbo
— Зрение GPT 4 Vision
— Работает в группах Telegram
— Нейросети /Midjourney, /StableDiffusion и Dalle 3 для генерации высококачественных изображений
— Возможность выбрать GPT личность для бота
— Возможность задать боту свою кастомную инструкцию
— Увеличенный х4 контекст и длина ответа бота
— Подключение бота к глобальной сети Интернет и использование полученной информации в своих ответах
— Доступ к бета версиям новых продуктов/нейросетей
— Все возможности Premium плана
— Отсутствует реклама

💯 <b>MAXIMUM</b>
— Безлимитный запросы на все функции.
— Вся функциональность бота доступна без ограничений.
— Работает в любых группах Telegram
— Отсутствует реклама
— Все функции прошлых подписок

<i>Функции /Midjourney, /StableDiffusion, /ask, GPT 4 Vision, редакции изображений в настоящее время недоступны.</i>""", parse_mode="HTML", reply_markup=await create_premium_buttons("monthly", "мес", 400, 700, 1200, 1700, 3900, "monthly"))
    else:
        await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())


@dp.message_handler(regexp="⚙️Настройки")
async def process_gpt(message: types.Message):
    username = message.from_user.first_name
    if await check_subscription(CHANNEL_ID, message.chat.id):
        user_id = message.chat.id
        db_context = await db.get_user_info(user_id, "context")
        db_voice = await db.get_user_info(user_id, "voice")
        db_context = db_context[0]
        db_voice = db_voice[0]
        await bot.send_message(message.chat.id, """В этом разделе вы можете изменить настройки:

1. Выбрать модель <b>GPT</b>
2. Выбрать роль для <b>ChatGPT</b>
3. Включить или отключить поддержку контекста. Когда контекст включен, бот учитывает свой предыдущий ответ для ведения диалога
4. Настроить голосовые ответы и выбрать голос <b>GPT</b>
(доступен в /premium)
""", parse_mode="HTML", reply_markup=await settings(db_context, db_voice))
    else:
        await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())


@dp.callback_query_handler(lambda call: call.data == "back_premium_call")
async def change_to_monthly(call: types.CallbackQuery):
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = """🤖 Бот предлагает бесплатный дневной лимит в 20 запросов (GPT 3.5) на создание текста и 1 запрос в день на работу с вашими изображениями для обеспечения оптимальной скорости и качества.

💠 Нужно больше запросов и более мощная и продвинутая версия бота <b>GPT-4</b> и <b>GPT-4 Turbo</b>? Тогда выберите одну из следующих доступных подписок, включающих дополнительную функциональность и расширенные лимиты, либо приобретите запросы отдельно:

👁‍🗨 <b>Mini</b>
— GPT 3.5 — 100 сообщений в день
— GPT 4 — 10 сообщения в день
— 5 изображений в день
— Нейросеть Dalle для генерации высококачественных изображений
— Отсутствует пауза между запросами
— Решение задач по фото
— Создание аниме по фото
— Отсутствует реклама

👌 <b>Starter:</b>
— GPT 3.5 — безлимитно
— GPT 4 — 30 сообщений в день
— 25 изображений в день
— 9 моделей GPT, включая GPT 4 Turbo
— Зрение GPT 4 Vision
— Решение задач по фото
— Нейросети /Midjourney, /StableDiffusion и Dalle  для генерации высококачественных изображений
— Редактор изображений на основе ИИ
— Создание аниме по фотографии
— Возможность выбрать GPT личность для бота
— Увеличенный х2 контекст и длина ответа бота
— Отсутствует реклама

🚀 <b>Premium:</b>
— GPT 3.5 — безлимитно
— GPT 4 — 50 сообщений в день
— 50 изображений в день
— 9 моделей GPT, включая GPT 4 Turbo
— Зрение GPT 4 Vision
— Работает в группах Telegram
— Создание аниме по фотографии
— Нейросети /Midjourney, /StableDiffusion и Dalle 3 для генерации высококачественных изображений
— Редактор изображений на основе ИИ
— Компьютерное зрение: распознование текста с фото, решение любых задач и экзаменационных билетов, любые запросы по тексту на фото.
— Голосовое управление, распознавание голосовых сообщений и режим ответа голосом
— Возможность выбрать GPT личность для бота
— Помнит больше сообщений в истории чата для более качественного ответа
— Увеличенный х3 контекст и длина ответа бота
— отсутствует реклама

🔥 <b>Ultra:</b>
— GPT 3.5 — безлимитно
— GPT 4 — 100 сообщений в день
— 100 изображений в день
— 9 моделей GPT, включая GPT 4 Turbo
— Зрение GPT 4 Vision
— Работает в группах Telegram
— Нейросети /Midjourney, /StableDiffusion и Dalle 3 для генерации высококачественных изображений
— Возможность выбрать GPT личность для бота
— Возможность задать боту свою кастомную инструкцию
— Увеличенный х4 контекст и длина ответа бота
— Подключение бота к глобальной сети Интернет и использование полученной информации в своих ответах
— Доступ к бета версиям новых продуктов/нейросетей
— Все возможности Premium плана
— Отсутствует реклама

💯 <b>MAXIMUM</b>
— Безлимитный запросы на все функции.
— Вся функциональность бота доступна без ограничений.
— Работает в любых группах Telegram
— Отсутствует реклама
— Все функции прошлых подписок

<i>Функции /Midjourney, /StableDiffusion, /ask, GPT 4 Vision, редакции изображений в настоящее время недоступны.</i>""", parse_mode="HTML", reply_markup=await create_premium_buttons("monthly", "мес", 400, 700, 1200, 1700, 3900, "monthly"))


@dp.callback_query_handler(lambda call: call.data == "sub_monthly")
async def change_to_monthly(call: types.CallbackQuery):
    try:
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await create_premium_buttons("monthly", "мес", 400, 700, 1200, 1700, 3900, "monthly"))
    except Exception as e:
        pass

@dp.callback_query_handler(lambda call: call.data == "sub_half_annual")
async def change_to_weekly(call: types.CallbackQuery):
    try:
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await create_premium_buttons("half_annual", "полгод", 1800, 3900, 7000, 9500, 22000, "half_annual"))
    except Exception as e:
        pass

@dp.callback_query_handler(lambda call: call.data == "sub_annual")
async def change_to_annual(call: types.CallbackQuery):
    try:
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await create_premium_buttons("annual", "год", 3400, 7600, 13000, 18000, 42000, "annual"))
    except Exception as e:
        pass

policy_rules =

public_rules =


@dp.callback_query_handler(lambda call: call.data == "maximum_half_annual")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"""💳Вы оформляете полугодовой тариф Maximum за ₽22000.

🔷Нажимая кнопку ниже, я даю согласие на регулярные списания, на обработку персональных данных и принимаю условия {public_rules} и {policy_rules}.""", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=await buy_maximum_half_annual_keyboard(user_id))

@dp.callback_query_handler(lambda call: call.data == "maximum_monthly")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"""💳Вы оформляете месячный тариф Maximum за ₽3900.

🔷Нажимая кнопку ниже, я даю согласие на регулярные списания, на обработку персональных данных и принимаю условия {public_rules} и {policy_rules}.""", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=await buy_maximum_monthly_keyboard(user_id))

@dp.callback_query_handler(lambda call: call.data == "maximum_annual")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"""💳Вы оформляете годовой тариф Maximum за ₽42000.

🔷Нажимая кнопку ниже, я даю согласие на регулярные списания, на обработку персональных данных и принимаю условия {public_rules} и {policy_rules}.""", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=await buy_maximum_annual_keyboard(user_id))

@dp.callback_query_handler(lambda call: call.data == "starter_half_annual")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"""💳Вы оформляете полугодовой тариф Starter за ₽3900.

🔷Нажимая кнопку ниже, я даю согласие на регулярные списания, на обработку персональных данных и принимаю условия {public_rules} и {policy_rules}.""", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=await buy_starter_half_annual_keyboard(user_id))

@dp.callback_query_handler(lambda call: call.data == "mini_half_annual")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"""💳Вы оформляете полугодовой тариф Mini за ₽1800.

🔷Нажимая кнопку ниже, я даю согласие на регулярные списания, на обработку персональных данных и принимаю условия {public_rules} и {policy_rules}.""", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=await buy_mini_half_annual_keyboard(user_id))

@dp.callback_query_handler(lambda call: call.data == "mini_monthly")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"""💳Вы оформляете месячный тариф Mini за ₽400.

🔷Нажимая кнопку ниже, я даю согласие на регулярные списания, на обработку персональных данных и принимаю условия {public_rules} и {policy_rules}.""", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=await buy_mini_monthly_keyboard(user_id))

@dp.callback_query_handler(lambda call: call.data == "mini_annual")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"""💳Вы оформляете годовой тариф Mini за ₽3400.

🔷Нажимая кнопку ниже, я даю согласие на регулярные списания, на обработку персональных данных и принимаю условия {public_rules} и {policy_rules}.""", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=await buy_mini_annual_keyboard(user_id))

@dp.callback_query_handler(lambda call: call.data == "premium_annual")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"""💳Вы оформляете годовой тариф Premium за ₽13000.

🔷Нажимая кнопку ниже, я даю согласие на регулярные списания, на обработку персональных данных и принимаю условия {public_rules} и {policy_rules}.""", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=await buy_premium_annual_keyboard(user_id))

@dp.callback_query_handler(lambda call: call.data == "premium_monthly")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"""💳Вы оформляете месячный тариф Premium за ₽1200.

🔷Нажимая кнопку ниже, я даю согласие на регулярные списания, на обработку персональных данных и принимаю условия {public_rules} и {policy_rules}.""", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=await buy_premium_monthly_keyboard(user_id))

@dp.callback_query_handler(lambda call: call.data == "starter_annual")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"""💳Вы оформляете годовой тариф Starter за ₽7600.

🔷Нажимая кнопку ниже, я даю согласие на регулярные списания, на обработку персональных данных и принимаю условия {public_rules} и {policy_rules}.""", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=await buy_starter_annual_keyboard(user_id))

@dp.callback_query_handler(lambda call: call.data == "starter_monthly")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"""💳Вы оформляете месячный тариф Starter за ₽700.

🔷Нажимая кнопку ниже, я даю согласие на регулярные списания, на обработку персональных данных и принимаю условия {public_rules} и {policy_rules}.""", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=await buy_starter_monthly_keyboard(user_id))

@dp.callback_query_handler(lambda call: call.data == "ultra_annual")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"""💳Вы оформляете годовой тариф Ultra за ₽18000.

🔷Нажимая кнопку ниже, я даю согласие на регулярные списания, на обработку персональных данных и принимаю условия {public_rules} и {policy_rules}.""", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=await buy_ultra_annual_keyboard(user_id))

@dp.callback_query_handler(lambda call: call.data == "ultra_monthly")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"""💳Вы оформляете месячный тариф Ultra за ₽1700.

🔷Нажимая кнопку ниже, я даю согласие на регулярные списания, на обработку персональных данных и принимаю условия {public_rules} и {policy_rules}.""", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=await buy_ultra_monthly_keyboard(user_id))

@dp.callback_query_handler(lambda call: call.data == "premium_half_annual")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"""💳Вы оформляете полугодовой тариф Premium за ₽7000.

🔷Нажимая кнопку ниже, я даю согласие на регулярные списания, на обработку персональных данных и принимаю условия {public_rules} и {policy_rules}.""", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=await buy_premium_half_annual_keyboard(user_id))

@dp.callback_query_handler(lambda call: call.data == "ultra_half_annual")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"""💳Вы оформляете полугодовой тариф Ultra за ₽9500.

🔷Нажимая кнопку ниже, я даю согласие на регулярные списания, на обработку персональных данных и принимаю условия {public_rules} и {policy_rules}.""", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=await buy_ultra_half_annual_keyboard(user_id))


@dp.callback_query_handler(lambda call: call.data == "change_gpt_model_call")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await check_user_sub(user_id)
    sub = await db.get_user_info(user_id, "sub")
    sub = sub[0]
    selected_model = await db.get_user_info(user_id, "selected_model")
    selected_model = selected_model[0]
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = """В боте доступны 9 моделей 🤖 Chat GPT:

<b>✅ gpt-3.5-turbo:</b> Это модель генерации текста, основанная на GPT-3.5 Turbo от OpenAI, предназначенная для чат-ботов и других приложений, где требуется контекстно-зависимая генерация языка.

<b>✅ gpt-3.5-turbo-1106:</b> Это обновленная версия chat gpt gpt-3.5-turbo, выпущенная 6 ноября. Соответствует предыдущей модели, но с улучшениями или обновлениями.

<b>✅ gpt-3.5-turbo-0613:</b> Представляет собой еще одну версию chat gpt gpt-3.5turbo, выпущенную 13 июня.

<b>✅ gpt-3.5-turbo-16k:</b> Это модификация модели gpt-3.5-turbo, которая была специально настроена для обработки больших объемов данных. Эта модель идеально подходит для ситуаций, когда необходимо генерировать большие объемы текста или обрабатывать очень длинные входные данные.

<b>✅ gpt-3.5-turbo-16k-0613:</b> Это обновленная версия модели gpt-3.5-turbo-16k, выпущенная 13 июня. Она обладает всеми преимуществами предыдущей модели, но включает в себя улучшения и обновления, сделанные по итогам последних исследований и отзывов пользователей.

<b>✅ gpt-3.5-turbo-instruct:</b> Модель GPT-3.5 Turbo, которая была специально обучена для выполнения инструкций, предоставленных в текстовых сообщениях.

<b>✅ gpt-3_5-turbo-instruct-0914:</b> Это версия модели gpt-3.5-turbo-instruct, выпущенная 14 сентября. Работает аналогично базовой модели, но может быть обновленной версией.

<b>🔥 gpt-4:</b> Модель генерации текста следующего поколения от OpenAI, основанная на структуре GPT-3, но с положительными улучшениями и оптимизациями.

<b>🔥 gpt-4-1106-preview:</b> Предварительный просмотр обновленной версии GPT-4, выпущенной 6 ноября.

<b>В бесплатной версии бота доступны все модели GPT 3.5.</b>

Пользователи с премиум-подпиской могут выбрать также любые модели <b>GPT 4</b>. Приобрести премиум-подписку /premium.
""", parse_mode="HTML", reply_markup=await gpt_s(selected_model, None))


@dp.callback_query_handler(lambda call: call.data == "context_on_call")
async def callback_buy(call: types.CallbackQuery):
    try:
        user_id = call.message.chat.id
        await db.set_context(user_id, "off")
        db_context = await db.get_user_info(user_id, "context")
        db_context = db_context[0]
        db_voice = await db.get_user_info(user_id, "voice")
        db_voice = db_voice[0]
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await settings(db_context, db_voice))
    except Exception as e:
        pass


@dp.callback_query_handler(lambda call: call.data == "context_off_call")
async def callback_buy(call: types.CallbackQuery):
    try:
        user_id = call.message.chat.id
        await db.set_context(user_id, "on")
        db_context = await db.get_user_info(user_id, "context")
        db_context = db_context[0]
        db_voice = await db.get_user_info(user_id, "voice")
        db_voice = db_voice[0]
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await settings(db_context, db_voice))
    except Exception as e:
        pass


@dp.callback_query_handler(lambda call: call.data == "voice_on_call")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await check_user_sub(user_id)
    sub = await db.get_user_info(user_id, "sub")
    sub = sub[0]

    if sub == "free" or sub == "starter" or sub == "mini":
        await bot.send_message(user_id, "⚠️ Эта функция доступна для /premium подписчиков.")
    elif sub == "premium" or sub == "ultra" or sub == "maximum":
        await db.set_voice(user_id, "off")
        voice_model = await db.get_user_info(user_id, "voice_model")
        voice = await db.get_user_info(user_id, "voice")
        voice = voice[0]
        voice_model = voice_model[0]
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await choose_voice_model(voice_model, None, voice))


@dp.callback_query_handler(lambda call: call.data == "voice_off_call")
async def callback_buy(call: types.CallbackQuery):
    user_id = call.message.chat.id
    await check_user_sub(user_id)
    sub = await db.get_user_info(user_id, "sub")
    sub = sub[0]

    if sub == "free" or sub == "starter" or sub == "mini":
        await bot.send_message(user_id, "⚠️ Эта функция доступна для /premium подписчиков.")
    elif sub == "premium" or sub == "ultra" or sub == "maximum":
        await db.set_voice(user_id, "on")
        voice_model = await db.get_user_info(user_id, "voice_model")
        voice = await db.get_user_info(user_id, "voice")
        voice = voice[0]
        voice_model = voice_model[0]
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await choose_voice_model(voice_model, None, voice))


@dp.callback_query_handler(lambda call: call.data == "check")
async def check_callback(call: types.CallbackQuery, state: FSMContext):
    await check(call)

async def check(call: types.CallbackQuery):
    chat_id = CHANNEL_ID
    user_id = call.message.chat.id
    chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=call.message.chat.id)

    if (chat_member.status in ["member", "administrator", "creator"] and
            chat_member.status in ["member", "administrator", "creator"]):
        if not await db.user_exists(user_id):
            await db.add_user(user_id)
        await bot.send_message(call.message.chat.id, """
Привет! 🤖👋

Наш бот предоставляет доступ к ChatGPT 3.5, ChatGPT 4 и DALL-E 3 для создания текстов и изображений.

Мы используем последние модели: GPT-4 Turbo, DALL-E 3, а также предыдущие версии GPT-4 и GPT 3.5 Turbo.

Здесь вы можете выполнять самые разнообразные задачи:

📝 Создание и изменение текстов.
💻 Написание и редактирование кода.
🌐 Перевод с любого языка.
🧠 Анализ и краткое изложение неструктурированного текста.
💬 Дружелюбный разговор и поддержка.
🎨 Создание графики по текстовым описаниям.
🌍 Быстрый поиск нужной информации.

✉️ Чтобы получить ответ, напишите свой вопрос в чат (выберите модель GPT в /settings).

🤖 Доступные команды:

/start — <i>Перезапустить бота</i>
/profile — <i>Мой профиль</i>
/premium — <i>Приобрести подписку</i>
/personality — <i>Выбрать роль GPT</i>
/deletecontext — <i>Обнулить контекст беседы</i>
/gptprompts – <i>руководство по написанию промптов для</i> <b>GPT</b>
/dalleprompts - <i>руководство по написанию промтов для</i> <b>DALL-E</b>
/settings — <i>Настройки</i>
/img (описание) — <i>Сгенерировать картинку по описанию (пример: /img дом возле моря)</i>
/info — <i>Возможности и команды</i>
/help — <i>Помощь</i>
/terms - <i>Условия использования</i>

📷 Если вы отправите боту фотографию, он может ее отредактировать, переделать в аниме, распознать текст, решить задание, ответить на ваш запрос по фото.

👨‍👨‍👧‍👦 Бот работает в группах (доступно на тарифе Premium). Чтобы задать ему вопрос в группе, используйте команду /ask "ваш запрос" (например, "/ask расскажи интересные факты о космосе").

❕Если бот вам не отвечает, перезапустите командой /start

Удачи! 🚀✨                             """, parse_mode="HTML", reply_markup=await main_kb(), disable_web_page_preview=True)
    else:
        await bot.send_message(call.message.chat.id, "Подпишитесь на канал!", reply_markup=await sub_channels())

@dp.callback_query_handler(lambda call: True)
async def process_call(call: types.CallbackQuery, state: FSMContext):
    action = call.data
    user_id = call.message.chat.id
    await check_user_sub(user_id)
    sub = await db.get_user_info(user_id, "sub")
    voice = await db.get_user_info(user_id, "voice")
    role = await db.get_user_info(user_id, "role_preview")
    voice_model = await db.get_user_info(user_id, "voice_model")
    sub = sub[0]
    role = role[0]
    voice = voice[0]
    voice_model = voice_model[0]


    models = {
    'gpt_3_5_turbo_call': "gpt-3.5-turbo",
    'gpt_3_5_turbo_1106_call': "gpt-3.5-turbo-1106",
    'gpt_3_5_turbo_0613_call': "gpt-3.5-turbo-0613",
    'gpt_3_5_turbo_16k_call': "gpt-3.5-turbo-16k",
    'gpt_3_5_turbo_16k_0613_call': "gpt-3.5-turbo-16k-0613",
    'gpt_3_5_turbo_instruct_call': "gpt-3.5-turbo-instruct",
    'gpt_3_5_turbo_instruct_0914_call': "gpt-3.5-turbo-instruct-0914",
    }

    models_4 = {
    'gpt_4_call': "gpt-4",
    'gpt_4_1106_preview_call': "gpt-4-1106-preview",
    }


    if action in models:
        model_call = models[action]
        await db.set_selected_model(user_id, model_call)
        try:
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await gpt_s(None,  model_call))
        except Exception as e:
            pass

    elif action in models_4:
        if sub != "free":
            model_call = models_4[action]
            await db.set_selected_model(user_id, model_call)
            try:
                await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await gpt_s(None,  model_call))
            except Exception as e:
                pass
        elif sub == "free":
            await bot.send_message(user_id, f"Вам недоступна данная модель! Для того чтобы пользоваться данной моделью необходимо преобрести подписку /premium.")


    role_mapping = {
    "default_role_call": "You helpful assistant",
    "add_role_call": "You advertising expert assistant",
    "hack_role_call": "You crazy, strange, intellectual, creative assistant",
    "seo_role_call": "You SEO specialist assistant",
    "psicho_role_call": "You psychologist assistant",
    "fullstack_role_call": "You full stack developer assistant",
    "codegen_role_call": "You code generator assistant",
    "tech_role_call": "You technical reference assistant",
    "repeater_role_call": "You tutor assistant",
    "news_role_call": "You news aggregator assistant",
    "textred_role_call": "You text editor assistant",
    "creative_role_call": "You creative writer assistant",
    "finance_role_call": "You Financial Consultant assistant",
    "twowords_role_call": "You briefly, in a nutshell assistant",
    }


    if action in role_mapping:
        text = role_mapping[action]
        name = action.split('_')[0]
        await db.set_role(user_id, text)
        await db.set_role_preview(user_id, name)
        try:
            if name in role_disc:
                text_role = role_disc[name]
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"<b>👤 Выберите роль для GPT:</b>\n\n{text_role}", parse_mode="HTML", reply_markup=await roles(name, None, None))
        except Exception as e:
            pass


    if action == "change_role_call":
        user_id = call.message.chat.id
        if role in role_disc:
            text_role = role_disc[role]
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"""<b>👤 Выберите роль для GPT:</b>\n\n{text_role}""", parse_mode="HTML", reply_markup=await roles(None, role, "on"))


    if action == "voice_setting_call":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="""В этом разделе вы можете включить режим голосового ответа и выбрать один из представленных голосов.

<b>Женские:</b> nova | shimmer
<b>Мужские:</b> alloy | echo | fable | onyx""", parse_mode="HTML", reply_markup=await choose_voice_model(voice_model, None, voice))

    voice_models = {
    'voice_alloy_call': "alloy",
    'voice_echo_call': "echo",
    'voice_fable_call': "fable",
    'voice_onyx_call': "onyx",
    'voice_nova_call': "nova",
    'voice_shimmer_call': "shimmer",
    }

    if action in voice_models:
        voice_call = voice_models[action]
        await db.set_voice_model(user_id, voice_call)
        try:
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=await choose_voice_model(None,  voice_call, voice))
        except Exception as e:
            pass


    if action == "voice_check_call":
        media = types.MediaGroup()
        media.attach_audio(types.InputFile('/path/Chatgpt/audio/alloy.mp3'))
        media.attach_audio(types.InputFile('/path/Chatgpt/audio/echo.mp3'))
        media.attach_audio(types.InputFile('/path/Chatgpt/audio/fable.mp3'))
        media.attach_audio(types.InputFile('/path/Chatgpt/audio/nova.mp3'))
        media.attach_audio(types.InputFile('/path/Chatgpt/audio/shimmer.mp3'))
        media.attach_audio(types.InputFile('/path/Chatgpt/audio/onyx.mp3'))
        await bot.send_media_group(call.message.chat.id, media=media)


    if action == "back_call":
        db_context = await db.get_user_info(user_id, "context")
        db_voice = await db.get_user_info(user_id, "voice")
        db_context = db_context[0]
        db_voice = db_voice[0]
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="""В этом разделе вы можете изменить настройки:

1. Выбрать модель <b>GPT</b>
2. Выбрать роль для <b>ChatGPT</b>
3. Включить или отключить поддержку контекста. Когда контекст включен, бот учитывает свой предыдущий ответ для ведения диалога
4. Настроить голосовые ответы и выбрать голос <b>GPT</b>
(доступен в /premium)
""", parse_mode="HTML", reply_markup=await settings(db_context, db_voice))


    if action == "photo_back_call":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="""Выберите необходимое действие

 Команды, помеченные "*", доступны только для /premium подписчиков.""", reply_markup=await photo_keyboard())


    if action == "photo_help_call":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="""🌟 Аниме — конвертирует Ваше фото в аниме.

<b>🧠 Решить сразу</b> — решает любые задание, экзаменационные билеты и отвечает на любые вопросы на фото.

<b>📝 Ввод запроса</b> — позволяет ввести необходимое действие, которое надо выполнить по тексту на фото.

<b>🕵️‍ Распознать</b> — распознает текст на фото.

<b>🚫 Удалить фон</b> — удаляет фон на фото.

<b>🔄 Заменить фон</b> — заменяет оригинальный фон изображения на указанный Вами.

<b>🗑️ Удалить текст</b> — удаляет текст на фото.

<b>🔍Супер-разрешение</b> — увеличивает разрешение фото в 4 раза.

<b>🌐 GPT-4 Vision</b> — зрение ИИ, которое полностью распознает фото и понимает что на нем изображено.""", parse_mode="HTML", reply_markup=await photo_back_keyboard(None))


@dp.message_handler(commands=['img'])
async def command_image(message: types.Message):
	username = message.from_user.first_name
	if await check_subscription(CHANNEL_ID, message.chat.id):
		text = message.text
		user_id = message.chat.id
		await check_user_sub(user_id)
		last_chat_id = message.message_id
		request_dalle = await db.get_user_info(user_id, "request_dalle")
		request_dalle = request_dalle[0]
		sub = await db.get_user_info(user_id, "sub")
		sub = sub[0]
		if sub == "free":
			dalle_model = "dall-e-2"
		elif sub != "free":
			dalle_model = "dall-e-3"
		await dalle_response(user_id, request_dalle, text, dalle_model, last_chat_id)
	else:
		await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def process_getting_answer(message: types.Message):
    username = message.from_user.first_name
    if await check_subscription(CHANNEL_ID, message.chat.id):
        user_id = message.chat.id
        await check_user_sub(user_id)
        last_chat_id = message.message_id
        photo = message.photo
        history = await db.get_user_info(user_id, "history")
        context = await db.get_user_info(user_id, "context")
        voice = await db.get_user_info(user_id, "voice")
        role = await db.get_user_info(user_id, "role")
        model = await db.get_user_info(user_id, "selected_model")
        sub = await db.get_user_info(user_id, "sub")
        voice_model = await db.get_user_info(user_id, "voice_model")
        history = history[0]
        context = context[0]
        voice = voice[0]
        role = role[0]
        model = model[0]
        sub = sub[0]
        voice_model = voice_model[0]

        if context == "on":
            text = (history or "") + message.text
        elif context == "off":
            text = message.text
        if model == "gpt-3.5-turbo-instruct" or model == "gpt-3.5-turbo-instruct-0914":
            text = message.text

        if voice == "on":
            text = message.text
            await voice_answer(user_id, voice_model, text)
        elif voice == "off":
            await gpt_answer(user_id, text, model, sub, role, last_chat_id)

    else:
        await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())

@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def handle_photo(message: types.Message):
    username = message.from_user.first_name
    if await check_subscription(CHANNEL_ID, message.chat.id):
        user_id = message.chat.id
        await check_user_sub(user_id)
        await bot.send_message(user_id, """Выберите необходимое действие

Команды, помеченные "*", доступны только для /premium подписчиков.""", reply_to_message_id=message.message_id , reply_markup=await photo_keyboard())

        photo = await bot.get_file(message.photo[-1].file_id)
        url = f'https://api.telegram.org/file/bot{TG_BOT_TOKEN}/{photo.file_path}'
        await db.set_photo_url(user_id, url)
        photo_data = await bot.download_file(photo.file_path)
        with open(f'/path/Chatgpt/photos/photo_{message.chat.id}.png', 'wb') as photo_file:
            photo_file.write(photo_data.read())

    else:
        await bot.send_message(message.chat.id, f"Здравствуйте, {username}\n\nДля начала подпишитесь👇", reply_markup=await sub_channels())


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)






