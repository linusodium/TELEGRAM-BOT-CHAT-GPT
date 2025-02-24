import datetime
import logging
import asyncio
import time
import pytz
import sys
import os

import aiogram
import openai

from datetime import timedelta
from aiogram.types.message import ContentType
from aiogram.types import CallbackQuery
from flask import Flask, request, jsonify
from yookassa import Configuration, Payment
from openai import AsyncOpenAI
from openai import OpenAI
from threading import Thread
from aiogram.types import InputFile
from config.Config import OPEN_AI_KEY
from dispatcher.Dispatcher import bot
from waitress import serve
from pathlib import Path
from database.db import db


app = Flask(__name__)


client = AsyncOpenAI(
     api_key=OPEN_AI_KEY,
)


async def check_subscription(chat_id, user_id):
    chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    return chat_member.status in ["member", "administrator", "creator"]


async def main():
    tz = pytz.timezone('Europe/Moscow')
    current_time = datetime.datetime.now(tz)

    desired_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)

    if current_time >= desired_time:
        desired_time += timedelta(days=1)

    time_difference = (desired_time - current_time).total_seconds()

    await asyncio.sleep(time_difference)

    await db.reset_request()
    await db.delete_history()


async def start_scheduler():
    while True:
        await main()
        await asyncio.sleep(86400)


class YooKassaPaymentProcessor:
    def __init__(self, account_id, secret_key):
        Configuration.account_id = account_id
        Configuration.secret_key = secret_key

    def create_payment(self, amount_value, currency, return_url, capture=True, description="", user_id=""):
        payment_data = {
            "amount": {
                "value": str(amount_value),
                "currency": currency
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": capture,
            "description": description,
            "metadata": {
                "user_id": user_id
            },
        }

        payment = Payment.create(payment_data)
        return payment.confirmation.confirmation_url


async def get_openai_response(text, model_name, role, chat_id) -> str:
    response = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": role,
            },
            {
                "role": "user",
                "content": text,
            }
        ],
        model=model_name,
        max_tokens=1500
    )
    ai_response = response.choices[0].message.content

    new_history = text + "\n" + ai_response + "\n"
    await db.add_history(chat_id, new_history)

    sub = await db.get_user_info(chat_id, "sub")
    sub = sub[0]

    last_history = await db.get_user_info(chat_id, "history")
    last_history = last_history[0]

    await process_history(chat_id, sub, last_history)

    return ai_response


async def process_history(chat_id, sub, last_history):
    subscription_costs = {
    "free": 5000,
    "mini": 5000,
    "starter": 10000,
    "premium": 15000,
    "ultra": 20000,
    "maximum": 20000
    }

    if sub in subscription_costs:
        total = subscription_costs[sub]
    else:
        total = 0

    if len(last_history) > total:
        last_history = last_history[1000:]
        await db.delete_history(chat_id)
        await db.add_history(chat_id, last_history)


async def get_openai_response_legacy(text, model_name, chat_id) -> str:
    response = await client.completions.create(
        prompt = text,
        model = model_name,
        max_tokens=1000
    )

    ai_response = response.choices[0].text

    return ai_response


async def get_gpt_4_vision_answer(text, file_url, user_id):
    response = await client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {
                        "type": "image_url",
                        "image_url": {"url": file_url}
                    }
                ]
            }],
            max_tokens=300
        )
    ai_response = response.choices[0].message.content

    return ai_response


async def openai_response_3_turbo(text, role, chat_id) -> str:
    return await get_openai_response(text, "gpt-3.5-turbo", role, chat_id)

async def openai_response_3_0301(text, role, chat_id) -> str:
    return await get_openai_response(text, "gpt-3.5-turbo-0301", role, chat_id)

async def openai_response_3_0613(text, role, chat_id) -> str:
    return await get_openai_response(text, "gpt-3.5-turbo-0613", role, chat_id)

async def openai_response_3_1106(text, role, chat_id) -> str:
    return await get_openai_response(text, "gpt-3.5-turbo-1106", role, chat_id)

async def openai_response_3_16k(text, role, chat_id) -> str:
    return await get_openai_response(text, "gpt-3.5-turbo-16k", role, chat_id)

async def openai_response_3_16k_0613(text, role, chat_id) -> str:
    return await get_openai_response(text, "gpt-3.5-turbo-16k-0613", role, chat_id)

async def openai_response_3_instruct(text, role, chat_id) -> str:
    return await get_openai_response_legacy(text, "gpt-3.5-turbo-instruct", chat_id)

async def openai_response_3_instruct_0914(text, role, chat_id) -> str:
    return await get_openai_response_legacy(text, "gpt-3.5-turbo-instruct-0914", chat_id)

async def openai_response_4(text, role, chat_id) -> str:
    return await get_openai_response(text, "gpt-4", role, chat_id)

async def openai_response_4_vision(text, role, chat_id) -> str:
    return await get_openai_response(text, "gpt-4-vision-preview", role, chat_id)

async def openai_response_4_turbo(text, role, chat_id) -> str:
    return await get_openai_response(text, "gpt-4-1106-preview", role, chat_id)


async def gpt_answer(chat_id, text, model, sub, role, last_chat_id):
    gpt_3_models = {
        "gpt-3.5-turbo": openai_response_3_turbo,
        "gpt-3.5-turbo-1106": openai_response_3_1106,
        "gpt-3.5-turbo-0613": openai_response_3_0613,
        "gpt-3.5-turbo-16k": openai_response_3_16k,
        "gpt-3.5-turbo-16k-0613": openai_response_3_16k_0613,
        "gpt-3.5-turbo-instruct": openai_response_3_instruct,
        "gpt-3.5-turbo-instruct-0914": openai_response_3_instruct_0914,
    }

    gpt_4_models = {
        "gpt-4": openai_response_4,
        "gpt-4-1106-preview": openai_response_4_turbo,
    }

    async def gpt_3(chat_id, text, model, role):
        if model in gpt_3_models:
            await get_answer(text, chat_id, gpt_3_models[model], role, last_chat_id)

    async def gpt_4(chat_id, text, model, role):
        if model in gpt_4_models:
            await get_answer(text, chat_id, gpt_4_models[model], role, last_chat_id)

    if sub in ["free", "starter", "premium", "ultra", "mini", "maximum"]:
        await gpt_3(chat_id, text, model, role)
    if sub in ["starter", "premium", "ultra", "mini", "maximum"]:
        await gpt_4(chat_id, text, model, role)


async def get_answer(text, chat_id, gpt_model, role, last_chat_id):
    try:
        request_gpt_3 = await db.get_user_info(chat_id, "request_gpt_3")
        request_gpt_4 = await db.get_user_info(chat_id, "request_gpt_4")
        model = await db.get_user_info(chat_id, "selected_model")
        request_gpt_3 = request_gpt_3[0]
        request_gpt_4 = request_gpt_4[0]
        model = model[0]

        gpt_3 = [
        'gpt-3.5-turbo',
        'gpt-3.5-turbo-1106',
        'gpt-3.5-turbo-0613',
        'gpt-3.5-turbo-16k',
        'gpt-3.5-turbo-16k-0613',
        'gpt-3.5-turbo-instruct',
        'gpt-3.5-turbo-instruct-0914',
        ]
        gpt_4 = ["gpt-4", "gpt-4-1106-preview"]

        if model in gpt_3 and request_gpt_3 != 0:
            wait_message = await bot.send_message(chat_id, "⏳Loading...", reply_to_message_id=last_chat_id)
            ai_response = await gpt_model(text, role, chat_id)
            result = await bot.edit_message_text(ai_response, chat_id, wait_message.message_id)
            if result:
                if request_gpt_3 > 0:
                    await db.minus_request(chat_id, 3)
                elif request_gpt_3 < 0:
                    pass
        elif model in gpt_3 and request_gpt_3 == 0:
            await bot.send_message(chat_id, "Ваш лимит запросов исчерпан❗️\nКупите подписку /premium или приходите завтра 📆")

        if model in gpt_4 and request_gpt_4 != 0:
            wait_message = await bot.send_message(chat_id, "⏳Loading...", reply_to_message_id=last_chat_id)
            ai_response = await gpt_model(text, role, chat_id)
            result = await bot.edit_message_text(ai_response, chat_id, wait_message.message_id)
            if result:
                if request_gpt_4 > 0:
                    await db.minus_request(chat_id, 4)
                elif request_gpt_4 < 0:
                    pass
        elif model in gpt_4 and request_gpt_4 == 0:
            await bot.send_message(chat_id, "Ваш лимит запросов исчерпан❗️\nКупите подписку /premium или приходите завтра 📆")
    except Exception as e:
        logging.exception(f"Произошла ошибка: {e}")


async def dalle_response(user_id, request_dalle, text, dalle_model, last_chat_id):
    if request_dalle != 0:
            try:
                if text == "/img":
                    await bot.send_message(user_id, "⚠️ Слишком короткий запрос для генерации изображения.")
                else:
                    await bot.send_message(user_id, """<b>✅ Вы добавлены в очередь.</b> Когда будет готово, мы отправим результат.
<i>*Это может занять ~1-5 минут, в зависимости от нагрузки</i>""", reply_to_message_id=last_chat_id, parse_mode="HTML")
                    prompt = text
                    model = dalle_model
                    response = await client.images.generate(
                        model="dall-e-3",
                        prompt=prompt,
                        size="1024x1024",
                        n=1,
                    )

                    image_url = response.data[0].url

                    result = await bot.send_photo(user_id, photo=image_url, caption="<b>Вот ваше изображение!</b>", parse_mode="HTML")
                    if result:
                        if request_dalle > 0:
                            await db.minus_request_dalle(user_id)
                        elif request_dalle < 0:
                            pass
            except Exception as e:
                logging.exception(f"Произошла ошибка: {e}")

    elif request_dalle == 0:
            await bot.send_message(user_id, "Ваш лимит исчерпан❗️\nКупите подписку /premium или приходите завтра 📆")


async def voice_answer(chat_id, voice_model, text):
    request_gpt_3 = await db.get_user_info(chat_id, "request_gpt_3")
    request_gpt_3 = request_gpt_3[0]
    if request_gpt_3 != 0:
        response = await client.audio.speech.create(
            model="tts-1",
            voice=voice_model,
            input=text,
        )

        output_file_path = "speech.mp3"
        response.stream_to_file(output_file_path)
        audio_input_file = InputFile(output_file_path)

        result = await bot.send_audio(chat_id=chat_id, audio=audio_input_file)

        if result:
            file_path = 'speech.mp3'
            os.remove(file_path)
            if request_gpt_3 > 0:
                await db.minus_request(chat_id, 3)
            elif request_gpt_3 < 0:
                pass
    elif request_gpt_3 == 0:
         await bot.send_message(user_id, "Ваш лимит исчерпан❗️\nКупите подписку /premium или приходите завтра 📆")


async def send_audios(chat_id, audio_files):
    for file in audio_files:
        await bot.send_audio(chat_id, InputFile(file))


async def set_requests(user_id, gpt_3, gpt_4, dalle):
    await db.set_request(user_id, gpt_3, "request_gpt_3")
    await db.set_request(user_id, gpt_4, "request_gpt_4")
    await db.set_request(user_id, dalle, "request_dalle")


def days_to_seconds(days):
    return days * 24 * 60 * 60


def time_sub_day(get_time):
    time_now = int(time.time())

    if get_time == 0:
        return None

    middle_time = int(get_time) - time_now

    if middle_time <= 0:
        return False
    else:
        dt = str(datetime.timedelta(seconds=middle_time))
        dt = dt.replace("days", "дней")
        dt = dt.replace("day", "день")
        return dt


async def check_user_sub(user_id):
    user_sub = time_sub_day(await db.get_time(user_id, "sub_time"))
    if user_sub == False:
        await db.set_sub(user_id, "free")
        await db.set_selected_model(user_id, "gpt-3.5-turbo")
        await set_requests(user_id, 20, 0, 1)
        await db.set_time_sub(user_id, 0)
    else:
        pass


async def sendMsg(user_id, sub):
    try:
        await bot.send_message(user_id, f"""<b>🎉 Поздравляем! Ваша подписка на ChatGPT успешно обновлена! 🚀</b> Готовьтесь к ещё большему потоку идей, креатива и вдохновения. <b>💬 Пусть каждое общение станет интересным и продуктивным </b>благодаря вашей подписке. 🌟 Наилучшие пожелания и продуктивных общений! 💡
""", parse_mode="HTML")
    except Exception as e:
        print(f"Произошла ошибка при отправке сообщения: {e}")


@app.route('/', methods=['POST'])
async def webhook():
    if request.method == 'POST':
        data = request.json
        user_id = data.get("object", {}).get("metadata", {}).get("user_id")
        status = data.get('object', {}).get('status')
        captured_at = data.get('object', {}).get('captured_at')
        event = data.get('event')
        description = data.get('object', {}).get('description')
        created_at = data.get('object', {}).get('created_at')
        loop = asyncio.get_event_loop()
        if event == "payment.succeeded":
            if description == "Подписка Starter на полгода":
                time_sub = int(time.time()) + days_to_seconds(182)
                await db.set_time_sub(user_id, time_sub)
                await db.set_sub(user_id, "starter")
                await set_requests(user_id, -1, 30, 25)
                await sendMsg(user_id, description)
            if description == "Подписка Maximum на месяц":
                time_sub = int(time.time()) + days_to_seconds(30)
                await db.set_time_sub(user_id, time_sub)
                await db.set_sub(user_id, "maximum")
                await set_requests(user_id, -1, -1, -1)
                await sendMsg(user_id, description)
            if description == "Подписка Maximum на полгода":
                time_sub = int(time.time()) + days_to_seconds(182)
                await db.set_time_sub(user_id, time_sub)
                await db.set_sub(user_id, "maximum")
                await set_requests(user_id, -1, -1, -1)
                await sendMsg(user_id, description)
            if description == "Подписка Maximum на год":
                time_sub = int(time.time()) + days_to_seconds(365)
                await db.set_time_sub(user_id, time_sub)
                await db.set_sub(user_id, "maximum")
                await set_requests(user_id, -1, -1, -1)
                await sendMsg(user_id, description)
            if description == "Подписка Mini на месяц":
                time_sub = int(time.time()) + days_to_seconds(30)
                await db.set_time_sub(user_id, time_sub)
                await db.set_sub(user_id, "mini")
                await set_requests(user_id, 100, 10, 5)
                await sendMsg(user_id, description)
            if description == "Подписка Mini на год":
                time_sub = int(time.time()) + days_to_seconds(365)
                await db.set_time_sub(user_id, time_sub)
                await db.set_sub(user_id, "mini")
                await set_requests(user_id, 100, 10, 5)
                await sendMsg(user_id, description)
            if description == "Подписка Mini на полгода":
                time_sub = int(time.time()) + days_to_seconds(182)
                await db.set_time_sub(user_id, time_sub)
                await db.set_sub(user_id, "mini")
                await set_requests(user_id, 100, 10, 5)
                await sendMsg(user_id, description)
            if description == "Подписка Premium на полгода":
                time_sub = int(time.time()) + days_to_seconds(182)
                await db.set_time_sub(user_id, time_sub)
                await db.set_sub(user_id, "premium")
                await set_requests(user_id, -1, 50, 50)
                await sendMsg(user_id, description)
            elif description == "Подписка Ultra на полгода":
                time_sub = int(time.time()) + days_to_seconds(182)
                await db.set_time_sub(user_id, time_sub)
                await db.set_sub(user_id, "ultra")
                await set_requests(user_id, -1, 100, 100)
                await sendMsg(user_id, description)
            elif description == "Подписка Premium на месяц":
                time_sub = int(time.time()) + days_to_seconds(30)
                await db.set_time_sub(user_id, time_sub)
                await db.set_sub(user_id, "premium")
                await set_requests(user_id, -1, 50, 50)
                await sendMsg(user_id, description)
            elif description == "Подписка Ultra на месяц":
                time_sub = int(time.time()) + days_to_seconds(30)
                await db.set_time_sub(user_id, time_sub)
                await db.set_sub(user_id, "ultra")
                await set_requests(user_id, -1, 100, 100)
                await sendMsg(user_id, description)
            elif description == "Подписка Starter на месяц":
                time_sub = int(time.time()) + days_to_seconds(30)
                await db.set_time_sub(user_id, time_sub)
                await db.set_sub(user_id, "starter")
                await set_requests(user_id, -1, 30, 25)
                await sendMsg(user_id, description)
            elif description == "Подписка Premium на год":
                time_sub = int(time.time()) + days_to_seconds(365)
                await db.set_time_sub(user_id, time_sub)
                await db.set_sub(user_id, "premium")
                await set_requests(user_id, -1, 50, 50)
                await sendMsg(user_id, description)
            elif description == "Подписка Ultra на год":
                time_sub = int(time.time()) + days_to_seconds(365)
                await db.set_time_sub(user_id, time_sub)
                await db.set_sub(user_id, "ultra")
                await set_requests(user_id, -1, 100, 100)
                await sendMsg(user_id, description)
            elif description == "Подписка Starter на год":
                time_sub = int(time.time()) + days_to_seconds(365)
                await db.set_time_sub(user_id, time_sub)
                await db.set_sub(user_id, "starter")
                await set_requests(user_id, -1, 30, 25)
                await sendMsg(user_id, description)
        else:
            print("ошибка")
        return jsonify({"success": True}), 200





