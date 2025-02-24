import asyncio
import sys

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from handlers.Handlers import YooKassaPaymentProcessor
from config.Config import YOKASSA_KEY, YOKASSA_SHOP


async def continue_b():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton('Продолжить'))
    return keyboard

async def choose_voice_model(voice_model, voice_call, voice):
    keyboard = InlineKeyboardMarkup(row_width=3)
    gpt_buttons = [
        {"model": "alloy", "callback": "voice_alloy_call"},
        {"model": "echo", "callback": "voice_echo_call"},
        {"model": "fable", "callback": "voice_fable_call"},
        {"model": "onyx", "callback": "voice_onyx_call"},
        {"model": "nova", "callback": "voice_nova_call"},
        {"model": "shimmer", "callback": "voice_shimmer_call"},
        ]
    for index, button_data in enumerate(gpt_buttons, start=1):
        callback = button_data["callback"]
        model = button_data["model"]

        if model == voice_call:
            model = "✅ " + model

        elif model == voice_model:
            model = "✅ " + model

        button = InlineKeyboardButton(model, callback_data=callback)
        globals()[f'item{index}'] = button

    keyboard.add(item1, item2, item3, item4, item5, item6)
    if voice == "off":
        keyboard.add(InlineKeyboardButton("❌ Голосовой ответ", callback_data="voice_off_call"))
    elif voice == "on":
        keyboard.add(InlineKeyboardButton("✅ Голосовой ответ", callback_data="voice_on_call"))
    keyboard.add(InlineKeyboardButton('Прослушать голоса', callback_data="voice_check_call"))
    keyboard.add(InlineKeyboardButton("⬅️Назад", callback_data="back_call"))

    return keyboard

async def choose_language():
    keyboard = InlineKeyboardMarkup()
    item2 = InlineKeyboardButton("", callback_data="rus_call")
    item2 = InlineKeyboardButton("", callback_data="eng_call")
    item2 = InlineKeyboardButton("", callback_data="")

async def sub_channels():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('⚠️Подписаться', url="https://t.me/it_neural"))
    keyboard.add(InlineKeyboardButton('✅Подписался', callback_data="check"))
    return keyboard

async def roles(name, role, status):
    button_data_list = [
        {"call": "default", "text": "Обычный 🔁", "callback_data": "default_role_call"},
        {"call": "add", "text": "Рекламный Эксперт 📣", "callback_data": "add_role_call"},
        {"call": "hack", "text": "Хакнутый GPT 👁‍🗨", "callback_data": "hack_role_call"},
        {"call": "seo", "text": "CEO специалист 👔", "callback_data": "seo_role_call"},
        {"call": "psicho", "text": "Психолог 🧘‍", "callback_data": "psicho_role_call"},
        {"call": "fullstack", "text": "Fullstack Разраб-ик 💻", "callback_data": "fullstack_role_call"},
        {"call": "codegen", "text": "Генератор Кода 💡", "callback_data": "codegen_role_call"},
        {"call": "tech", "text": "Техн-ий Справочник 📚", "callback_data": "tech_role_call"},
        {"call": "repeater", "text": "Репетитор 🎓", "callback_data": "repeater_role_call"},
        {"call": "news", "text": "Новостной Агрегатор 🌐", "callback_data": "news_role_call"},
        {"call": "textred", "text": "Редактор Текста 📝", "callback_data": "textred_role_call"},
        {"call": "creative", "text": "Писатель Статей ✍️", "callback_data": "creative_role_call"},
        {"call": "finance", "text": "Финан-ый Консультант 💰", "callback_data": "finance_role_call"},
        {"call": "twowords", "text": "Кратко ⏩", "callback_data": "twowords_role_call"},
    ]

    keyboard = InlineKeyboardMarkup(row_width=2)

    for index, button_data in enumerate(button_data_list, start=1):
        callback_data = button_data["callback_data"]
        text = button_data["text"]
        call = button_data["call"]


        if call == name:
            text = "✅ " + text

        elif call == role:
            text = "✅ " + text

        button = InlineKeyboardButton(text, callback_data=callback_data)
        globals()[f'item{index}'] = button

    keyboard.add(item1, item2, item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13, item14)
    if status == "on":
        keyboard.add(InlineKeyboardButton("⬅️Назад", callback_data="back_call"))
    else:
        pass

    return keyboard

async def gpt_s(selected_model, model_call):
    keyboard = InlineKeyboardMarkup(row_width=1)
    gpt_buttons = [
        {"model": "gpt-3.5-turbo", "callback": "gpt_3_5_turbo_call"},
        {"model": "gpt-3.5-turbo-1106", "callback": "gpt_3_5_turbo_1106_call"},
        {"model": "gpt-3.5-turbo-0613", "callback": "gpt_3_5_turbo_0613_call"},
        {"model": "gpt-3.5-turbo-16k", "callback": "gpt_3_5_turbo_16k_call"},
        {"model": "gpt-3.5-turbo-16k-0613", "callback": "gpt_3_5_turbo_16k_0613_call"},
        {"model": "gpt-3.5-turbo-instruct", "callback": "gpt_3_5_turbo_instruct_call"},
        {"model": "gpt-3.5-turbo-instruct-0914", "callback": "gpt_3_5_turbo_instruct_0914_call"},
        {"model": "gpt-4", "callback": "gpt_4_call"},
        {"model": "gpt-4-1106-preview", "callback": "gpt_4_1106_preview_call"}
        ]
    for index, button_data in enumerate(gpt_buttons, start=1):
        callback = button_data["callback"]
        model = button_data["model"]

        if model_call == model:
            model = "✅ " + model

        elif model == selected_model:
            model = "✅ " + model

        button = InlineKeyboardButton(model, callback_data=callback)
        globals()[f'item{index}'] = button

    keyboard.add(item1, item2, item3, item4, item5, item6, item7, item8, item9)
    keyboard.add(InlineKeyboardButton("⬅️Назад", callback_data="back_call"))
    return keyboard

async def settings(db_context, db_voice):
    keyboard = InlineKeyboardMarkup(row_width=1)
    item1 = InlineKeyboardButton("🤖 Выбрать модель GPT", callback_data="change_gpt_model_call")
    item2 = InlineKeyboardButton("🎭 Выбрать GPT - Роль", callback_data="change_role_call")

    if db_context == "off":
        item3 = InlineKeyboardButton("❌ Поддержка контекста", callback_data="context_off_call")
    elif db_context == "on":
        item3 = InlineKeyboardButton("✅ Поддержка контекста", callback_data="context_on_call")
    item4 = InlineKeyboardButton("🔊 Голосовой ответ", callback_data="voice_setting_call")
    if db_voice == "on":
        item4.text = "🔊 Голосовой ответ"
    elif db_voice == "off":
        item4.text = "🔇 Голосовой ответ"

    keyboard.add(item1, item3, item2, item4)
    return keyboard

async def main_kb():
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=False, row_width=3, resize_keyboard=True)
    item1 = KeyboardButton('👤Мой профиль')
    item2 = KeyboardButton('⚙️Настройки')
    item3 = KeyboardButton('🎭GPT - Роли')
    keyboard.add(item1, item2, item3)
    keyboard.add(KeyboardButton('🚀Премиум подписка'))
    return keyboard


yookassa_processor = YooKassaPaymentProcessor(YOKASSA_SHOP, YOKASSA_KEY)


async def payment_1_fun(user_id):
    payment_1 = yookassa_processor.create_payment(amount_value=400.00, currency="RUB", return_url="https://t.me/it_neural_bot", description="Подписка Mini на месяц", user_id=user_id)
    return payment_1
async def payment_2_fun(user_id):
    payment_2 = yookassa_processor.create_payment(amount_value=700.00, currency="RUB", return_url="https://t.me/it_neural_bot", description="Подписка Starter на месяц", user_id=user_id)
    return payment_2
async def payment_3_fun(user_id):
    payment_3 = yookassa_processor.create_payment(amount_value=1200.00, currency="RUB", return_url="https://t.me/it_neural_bot", description="Подписка Premium на месяц", user_id=user_id)
    return payment_3
async def payment_4_fun(user_id):
    payment_4 = yookassa_processor.create_payment(amount_value=1700.00, currency="RUB", return_url="https://t.me/it_neural_bot", description="Подписка Ultra на месяц", user_id=user_id)
    return payment_4
async def payment_5_fun(user_id):
    payment_5 = yookassa_processor.create_payment(amount_value=3900.00, currency="RUB", return_url="https://t.me/it_neural_bot", description="Подписка Maximum на месяц", user_id=user_id)
    return payment_5
async def payment_6_fun(user_id):
    payment_6 = yookassa_processor.create_payment(amount_value=1800.00, currency="RUB", return_url="https://t.me/it_neural_bot", description="Подписка Mini на полгода", user_id=user_id)
    return payment_6
async def payment_7_fun(user_id):
    payment_7 = yookassa_processor.create_payment(amount_value=3900.00, currency="RUB", return_url="https://t.me/it_neural_bot", description="Подписка Starter на полгода", user_id=user_id)
    return payment_7
async def payment_8_fun(user_id):
    payment_8 = yookassa_processor.create_payment(amount_value=7000.00, currency="RUB", return_url="https://t.me/it_neural_bot", description="Подписка Premium на полгода", user_id=user_id)
    return payment_8
async def payment_9_fun(user_id):
    payment_9 = yookassa_processor.create_payment(amount_value=9500.00, currency="RUB", return_url="https://t.me/it_neural_bot", description="Подписка Ultra на полгода", user_id=user_id)
    return payment_9
async def payment_10_fun(user_id):
    payment_10 = yookassa_processor.create_payment(amount_value=22000.00, currency="RUB", return_url="https://t.me/it_neural_bot", description="Подписка Maximum на полгода", user_id=user_id)
    return payment_10
async def payment_11_fun(user_id):
    payment_11 = yookassa_processor.create_payment(amount_value=3400.00, currency="RUB", return_url="https://t.me/it_neural_bot", description="Подписка Mini на год", user_id=user_id)
    return payment_11
async def payment_12_fun(user_id):
    payment_12 = yookassa_processor.create_payment(amount_value=7600.00, currency="RUB", return_url="https://t.me/it_neural_bot", description="Подписка Starter на год", user_id=user_id)
    return payment_12
async def payment_13_fun(user_id):
    payment_13 = yookassa_processor.create_payment(amount_value=13000.00, currency="RUB", return_url="https://t.me/it_neural_bot", description="Подписка Premium на год", user_id=user_id)
    return payment_13
async def payment_14_fun(user_id):
    payment_14 = yookassa_processor.create_payment(amount_value=18000.00, currency="RUB", return_url="https://t.me/it_neural_bot", description="Подписка Ultra на год", user_id=user_id)
    return payment_14
async def payment_15_fun(user_id):
    payment_15 = yookassa_processor.create_payment(amount_value=42000.00, currency="RUB", return_url="https://t.me/it_neural_bot", description="Подписка Maximum на год", user_id=user_id)
    return payment_15


async def create_payment_keyboard(amount, url):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(f"Оплатить ₽{amount}", url=url))
    keyboard.add(InlineKeyboardButton('⬅️Назад', callback_data="back_premium_call"))
    return keyboard

# Тариф Mini, Месячная оплата
async def buy_mini_monthly_keyboard(user_id):
    buy_mini_monthly_keyboard = await create_payment_keyboard(400, await payment_1_fun(user_id))
    return buy_mini_monthly_keyboard

# Тариф Starter, Месячная оплата
async def buy_starter_monthly_keyboard(user_id):
    buy_starter_monthly_keyboard = await create_payment_keyboard(700, await payment_2_fun(user_id))
    return buy_starter_monthly_keyboard

# Тариф Premium, Месячная оплата
async def buy_premium_monthly_keyboard(user_id):
    buy_premium_monthly_keyboard = await create_payment_keyboard(1200, await payment_3_fun(user_id))
    return buy_premium_monthly_keyboard

# Тариф Ultra, Месячная оплата
async def buy_ultra_monthly_keyboard(user_id):
    buy_ultra_monthly_keyboard = await create_payment_keyboard(1700, await payment_4_fun(user_id))
    return buy_ultra_monthly_keyboard

# Тариф Maximum, Месячная оплата
async def buy_maximum_monthly_keyboard(user_id):
    buy_maximum_monthly_keyboard = await create_payment_keyboard(3900, await  payment_5_fun(user_id))
    return buy_maximum_monthly_keyboard

# Тариф Mini, Полгодовая оплата
async def buy_mini_half_annual_keyboard(user_id):
    buy_mini_half_annual_keyboard = await create_payment_keyboard(1800, await payment_6_fun(user_id))
    return buy_mini_half_annual_keyboard

# Тариф Starter, Полгодовая оплата
async def buy_starter_half_annual_keyboard(user_id):
    buy_starter_half_annual_keyboard = await create_payment_keyboard(3900, await  payment_7_fun(user_id))
    return buy_starter_half_annual_keyboard

# Тариф Premium, Полгодовая оплата
async def buy_premium_half_annual_keyboard(user_id):
    buy_premium_half_annual_keyboard = await create_payment_keyboard(7000, await payment_8_fun(user_id))
    return buy_premium_half_annual_keyboard

# Тариф Ultra, Полгодовая оплата
async def buy_ultra_half_annual_keyboard(user_id):
    buy_ultra_half_annual_keyboard = await create_payment_keyboard(9500, await payment_9_fun(user_id))
    return buy_ultra_half_annual_keyboard

# Тариф Maximum, Полгодовая оплата
async def buy_maximum_half_annual_keyboard(user_id):
    buy_maximum_half_annual_keyboard = await create_payment_keyboard(22000, await payment_10_fun(user_id))
    return buy_maximum_half_annual_keyboard

# Тариф Mini, Годовая оплата
async def buy_mini_annual_keyboard(user_id):
    buy_mini_annual_keyboard = await create_payment_keyboard(3400, await payment_11_fun(user_id))
    return buy_mini_annual_keyboard

# Тариф Starter, Годовая оплата
async def buy_starter_annual_keyboard(user_id):
    buy_starter_annual_keyboard = await create_payment_keyboard(7600, await payment_12_fun(user_id))
    return buy_starter_annual_keyboard

# Тариф Premium, Годовая оплата
async def buy_premium_annual_keyboard(user_id):
    buy_premium_annual_keyboard = await create_payment_keyboard(13000, await payment_13_fun(user_id))
    return buy_premium_annual_keyboard

# Тариф Ultra, Годовая оплата
async def buy_ultra_annual_keyboard(user_id):
    buy_ultra_annual_keyboard = await create_payment_keyboard(18000, await payment_14_fun(user_id))
    return buy_ultra_annual_keyboard

# Тариф Maximum, Годовая оплата
async def buy_maximum_annual_keyboard(user_id):
    buy_maximum_annual_keyboard = await create_payment_keyboard(42000, await payment_15_fun(user_id))
    return buy_maximum_annual_keyboard


async def photo_back_keyboard(status):
    keyboard = InlineKeyboardMarkup(row_width=1)
    item1 = InlineKeyboardButton("⬅️Назад", callback_data="photo_back_call")
    if status == "on":
        item1.text = "Отмена"
    keyboard.add(item1)
    return keyboard

async def photo_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    item1 = InlineKeyboardButton("🌟 Аниме", callback_data="photo_anime_call")
    item2 = InlineKeyboardButton("🧠 Решить задачу", callback_data="photo_math_call")
    item3 = InlineKeyboardButton("📝 Ввод запроса", callback_data="photo_input_call")
    item4 = InlineKeyboardButton("🕵️‍ Распознать", callback_data="photo_detect_call")
    item5 = InlineKeyboardButton("🚫 Удалить фон*", callback_data="photo_erase_call")
    item6 = InlineKeyboardButton("🔄 Заменить фон*", callback_data="photo_change_call")
    item7 = InlineKeyboardButton("🗑️ Удалить текст*", callback_data="photo_deletetext_call")
    item8 = InlineKeyboardButton("🔍 Супер-разрешение*", callback_data="photo_resolution_call")

    keyboard.add(item1, item2, item3, item4, item5, item6, item7, item8)

    keyboard.add(InlineKeyboardButton("🌐 GPT-4 Vision*", callback_data="photo_gpt4vision_call"))
    keyboard.add(InlineKeyboardButton("❓ Помощь", callback_data="photo_help_call"))

    return keyboard

async def create_premium_buttons(plan, plan_price, mini_price, starter_price, premium_price, ultra_price, maximum_price, selected_plan):
    keyboard = InlineKeyboardMarkup(row_width=3)
    item_monthly = InlineKeyboardButton("Месячная", callback_data="sub_monthly")
    item_half_annual = InlineKeyboardButton("Полугодовая", callback_data="sub_half_annual")
    item_annual = InlineKeyboardButton("Годовая", callback_data="sub_annual")

    if plan == selected_plan:
        item_monthly.text = "🟢Месячная" if plan == "monthly" else "Месячная"
        item_half_annual.text = "🟢Полугодовая" if plan == "half_annual" else "Полугодовая"
        item_annual.text = "🟢Годовая" if plan == "annual" else "Годовая"

    keyboard.add(item_monthly, item_half_annual, item_annual)
    if selected_plan == "half_annual":
        keyboard.add(InlineKeyboardButton(f"👁‍🗨 Mini: ₽{mini_price}/{plan_price}", callback_data=f"mini_{plan}"))
        keyboard.add(InlineKeyboardButton(f"👌 Starter: ₽{starter_price}/{plan_price}", callback_data=f"starter_{plan}"))
        keyboard.add(InlineKeyboardButton(f"🚀 Premium: ₽{premium_price}/{plan_price}", callback_data=f"premium_{plan}"))
        keyboard.add(InlineKeyboardButton(f"🔥 Ultra: ₽{ultra_price}/{plan_price}", callback_data=f"ultra_{plan}"))
        keyboard.add(InlineKeyboardButton(f"💯 Maximum: ₽{maximum_price}/{plan_price}", callback_data=f"maximum_{plan}"))
    elif selected_plan == "monthly":
        keyboard.add(InlineKeyboardButton(f"👁‍🗨 Mini: ₽{mini_price}/{plan_price}", callback_data=f"mini_{plan}"))
        keyboard.add(InlineKeyboardButton(f"👌 Starter: ₽{starter_price}/{plan_price}", callback_data=f"starter_{plan}"))
        keyboard.add(InlineKeyboardButton(f"🚀 Premium: ₽{premium_price}/{plan_price}", callback_data=f"premium_{plan}"))
        keyboard.add(InlineKeyboardButton(f"🔥 Ultra: ₽{ultra_price}/{plan_price}", callback_data=f"ultra_{plan}"))
        keyboard.add(InlineKeyboardButton(f"💯 Maximum: ₽{maximum_price}/{plan_price}", callback_data=f"maximum_{plan}"))
    elif selected_plan == "annual":
        keyboard.add(InlineKeyboardButton(f"👁‍🗨 Mini: ₽{mini_price}/{plan_price}", callback_data=f"mini_{plan}"))
        keyboard.add(InlineKeyboardButton(f"👌 Starter: ₽{starter_price}/{plan_price}", callback_data=f"starter_{plan}"))
        keyboard.add(InlineKeyboardButton(f"🚀 Premium: ₽{premium_price}/{plan_price}", callback_data=f"premium_{plan}"))
        keyboard.add(InlineKeyboardButton(f"🔥 Ultra: ₽{ultra_price}/{plan_price}", callback_data=f"ultra_{plan}"))
        keyboard.add(InlineKeyboardButton(f"💯 Maximum: ₽{maximum_price}/{plan_price}", callback_data=f"maximum_{plan}"))

    return keyboard
