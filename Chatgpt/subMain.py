import aiogram
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ParseMode
from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config.Config import SUB_MAIN_BOT_TOKEN
from config.Config import SUB_MAIN_IDS
from handlers.Handlers import *
from database.db import db


bot = Bot(token=SUB_MAIN_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class DelUser(StatesGroup):
    stepOne = State()
    stepTwo = State()

class MinusSub(StatesGroup):
    stepOne = State()
    stepTwo = State()

class PlusSub(StatesGroup):
    stepOne = State()
    stepTwo = State()
    stepThree = State()
    stepFour = State()


async def subMain_kb():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton('Выдать подписку'))
    keyboard.add(KeyboardButton('Просмотреть статистику'))
    keyboard.add(KeyboardButton('Удалить пользователя'))
    keyboard.add(KeyboardButton('Лишить подписки'))
    return keyboard

async def subs():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    item1 = KeyboardButton('mini')
    item2 = KeyboardButton('starter')
    item3 = KeyboardButton('premium')
    item5 = KeyboardButton('maximum')
    item4 = KeyboardButton('ultra')
    keyboard.add(item1, item2, item3, item4, item5)
    return keyboard

async def sub_time():
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    item1 = KeyboardButton('месяц')
    item2 = KeyboardButton('полгода')
    item3 = KeyboardButton('год')
    keyboard.add(item1, item2, item3)
    return keyboard


@dp.message_handler(commands=['help'])
async def start(message: types.Message):
    user_id = message.chat.id
    await bot.send_message(user_id, """<i>Для отмены любого действия - Stop</i>""", parse_mode="HTML")

@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    if str(user_id) in SUB_MAIN_IDS:
        await bot.send_message(user_id, """<b>Админ-панель. Выберете действие:</b>""", parse_mode="HTML", reply_markup=await subMain_kb())


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def process_getting_answer(message: types.Message, state: FSMContext):
    user_text = message.text
    user_id = message.chat.id
    if user_text == "Выдать подписку":
        await PlusSub.stepOne.set()
        await bot.send_message(user_id, "<b>Введите ID пользователя:</b>", parse_mode="HTML")
    elif user_text == "Просмотреть статистику":
        free = await db.get_sub_count("free")
        mini = await db.get_sub_count("mini")
        starter = await db.get_sub_count("starter")
        premium = await db.get_sub_count("premium")
        ultra = await db.get_sub_count("ultra")
        maximum = await db.get_sub_count("maximum")
        sub_sum = mini + starter + premium + ultra + maximum
        await bot.send_message(user_id, f"""<b>Количество пользователей без подписки:</b> {free}
<b>Количество пользователей с подпиской:</b> {sub_sum}
<b>Количество пользователей с mini:</b> {mini}
<b>Количество пользователей c starter:</b> {starter}
<b>Количество пользователей c premium:</b> {premium}
<b>Количество пользователей c ultra:</b> {ultra}
<b>Количество пользователей c maximum:</b> {maximum}
""", parse_mode="HTML")
    elif user_text == "Удалить пользователя":
        await DelUser.stepOne.set()
        await bot.send_message(user_id, "<b>Введите ID пользователя:</b>", parse_mode="HTML")
    elif user_text == "Лишить подписки":
        await MinusSub.stepOne.set()
        await bot.send_message(user_id, "<b>Введите ID пользователя:</b>", parse_mode="HTML")
    else:
        await bot.send_message(user_id, "<b>Ошибка:</b> Неверное действие!", parse_mode="HTML")


@dp.message_handler(state=DelUser.stepOne)
async def some_state_handler(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    user_sub_id = message.text
    users_ids = await db.get_all_user_ids()
    if str(user_sub_id) in str(users_ids):
        await state.finish()
        await DelUser.stepTwo.set()
        await state.update_data(user_sub_id=user_sub_id)
        await bot.send_message(user_id, f"<b>Пользователь</b> <i>{user_sub_id}</i> <b>будет удалён из базы данных.</b>\n\n<b>Хотите продолжить?</b> [Д/н]", parse_mode="HTML")
    elif user_sub_id == "Stop":
        await state.finish()
        await bot.send_message(user_id, """<b>Выберете действие:</b>""", parse_mode="HTML", reply_markup=await subMain_kb())
    else:
        await bot.send_message(user_id, "<b>Ошибка:</b> Пользователь не найден!", parse_mode="HTML")

@dp.message_handler(state=DelUser.stepTwo)
async def some_state_handler(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    user_text = message.text
    saved_data = await state.get_data()
    user_sub_id = saved_data.get('user_sub_id')

    if user_text == "Д" or user_text == "д" or user_text == "Y" or user_text == "y":
        await state.finish()
        await db.delete_user(user_sub_id)
        await bot.send_message(user_id, """Пользователь был удалён из базы.""")
        await bot.send_message(user_id, """<b>Выберете действие:</b>""", parse_mode="HTML", reply_markup=await subMain_kb())
    elif user_text == "Н" or user_text == "н" or user_text == "N" or user_text == "n":
        await state.finish()
        await bot.send_message(user_id, """Прервано.""", parse_mode="HTML")
        await bot.send_message(user_id, """<b>Выберете действие:</b>""", parse_mode="HTML", reply_markup=await subMain_kb())
    else:
        await state.finish()
        await bot.send_message(user_id, """Прервано.""", parse_mode="HTML")
        await bot.send_message(user_id, """<b>Выберете действие:</b>""", parse_mode="HTML", reply_markup=await subMain_kb())


@dp.message_handler(state=MinusSub.stepOne)
async def some_state_handler(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    user_sub_id = message.text
    users_ids = await db.get_all_user_ids()
    if str(user_sub_id) in str(users_ids):
        await state.finish()
        await MinusSub.stepTwo.set()
        await state.update_data(user_sub_id=user_sub_id)
        await bot.send_message(user_id, f"<b>Пользователь</b> <i>{user_sub_id}</i> <b>будет лишен подписки.</b>\n\n<b>Хотите продолжить?</b> [Д/н]", parse_mode="HTML")
    elif user_sub_id == "Stop":
        await state.finish()
        await bot.send_message(user_id, """<b>Выберете действие:</b>""", parse_mode="HTML", reply_markup=await subMain_kb())
    else:
        await bot.send_message(user_id, "<b>Ошибка:</b> Пользователь не найден!", parse_mode="HTML")

@dp.message_handler(state=MinusSub.stepTwo)
async def some_state_handler(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    user_text = message.text
    saved_data = await state.get_data()
    user_sub_id = saved_data.get('user_sub_id')

    if user_text == "Д" or user_text == "д" or user_text == "Y" or user_text == "y":
        await state.finish()
        await db.minus_user_sub(user_sub_id)
        await bot.send_message(user_id, """Пользователь был лишен подписки.""")
        await bot.send_message(user_id, """<b>Выберете действие:</b>""", parse_mode="HTML", reply_markup=await subMain_kb())
    elif user_text == "Н" or user_text == "н" or user_text == "N" or user_text == "n":
        await state.finish()
        await bot.send_message(user_id, """Прервано.""", parse_mode="HTML")
        await bot.send_message(user_id, """<b>Выберете действие:</b>""", parse_mode="HTML", reply_markup=await subMain_kb())
    else:
        await state.finish()
        await bot.send_message(user_id, """Прервано.""", parse_mode="HTML")
        await bot.send_message(user_id, """<b>Выберете действие:</b>""", parse_mode="HTML", reply_markup=await subMain_kb())


@dp.message_handler(state=PlusSub.stepOne)
async def some_state_handler(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    user_sub_id = message.text
    users_ids = await db.get_all_user_ids()
    if str(user_sub_id) in str(users_ids):
        await state.finish()
        await PlusSub.stepTwo.set()
        await state.update_data(user_sub_id=user_sub_id)
        await bot.send_message(user_id, "<b>Выберите подписку:</b>", parse_mode="HTML", reply_markup=await subs())
    elif user_sub_id == "Stop":
        await state.finish()
        await bot.send_message(user_id, """<b>Выберете действие:</b>""", parse_mode="HTML", reply_markup=await subMain_kb())
    else:
        await bot.send_message(user_id, "<b>Ошибка:</b> Пользователь не найден!", parse_mode="HTML")

@dp.message_handler(state=PlusSub.stepTwo)
async def some_state_handler(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    user_sub = message.text
    subs = ["mini", "starter", "premium", "ultra", "maximum"]
    if user_sub in subs:
        saved_data = await state.get_data()
        user_sub_id = saved_data.get('user_sub_id')
        await state.finish()
        await PlusSub.stepThree.set()
        await state.update_data(user_sub=user_sub)
        await state.update_data(user_sub_id=user_sub_id)
        await bot.send_message(user_id, "<b>Выберите время подписки:</b>", parse_mode="HTML", reply_markup=await sub_time())
    elif user_sub == "Stop":
        await state.finish()
        await bot.send_message(user_id, """<b>Выберете действие:</b>""", parse_mode="HTML", reply_markup=await subMain_kb())
    else:
        await bot.send_message(user_id, "<b>Ошибка:</b> Неверная подписка!", parse_mode="HTML")

@dp.message_handler(state=PlusSub.stepThree)
async def some_state_handler(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    sub_time = message.text
    saved_data = await state.get_data()
    user_sub_id = saved_data.get('user_sub_id')
    user_sub = saved_data.get('user_sub')
    times = ["месяц", "полгода", "год"]
    if sub_time in times:
        if sub_time == "месяц":
            time_sub = int(time.time()) + days_to_seconds(30)
        elif sub_time == "полгода":
            time_sub = int(time.time()) + days_to_seconds(182)
        elif sub_time == "год":
            time_sub = int(time.time()) + days_to_seconds(365)
        await state.finish()
        await PlusSub.stepFour.set()
        await state.update_data(user_sub=user_sub)
        await state.update_data(time_sub=time_sub)
        await state.update_data(user_sub_id=user_sub_id)
        await state.update_data(sub_time=sub_time)
        await bot.send_message(user_id, f"<b>Пользователь:</b> {user_sub_id}\n<b>Подписка:</b> {user_sub}\n<b>Время подписки:</b> {sub_time}\n\n<b>Хотите продолжить?</b> [Д/н]", parse_mode="HTML")
    elif sub_time == "Stop":
        await state.finish()
        await bot.send_message(user_id, """<b>Выберете действие:</b>""", parse_mode="HTML", reply_markup=await subMain_kb())
    else:
        await bot.send_message(user_id, "<b>Ошибка:</b> Неправильное время!", parse_mode="HTML")

@dp.message_handler(state=PlusSub.stepFour)
async def some_state_handler(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    user_text = message.text
    saved_data = await state.get_data()
    user_sub_id = saved_data.get('user_sub_id')
    user_sub = saved_data.get('user_sub')
    time_sub = saved_data.get('time_sub')

    if user_text == "Д" or user_text == "д" or user_text == "Y" or user_text == "y":
        await db.set_sub(user_sub_id, user_sub)
        await db.set_time_sub(user_sub_id, time_sub)
        await add_requests(user_sub_id, user_sub)
        await bot.send_message(user_id, "<b>Подписка была успешно выдана!</b>", parse_mode="HTML")
        await state.finish()
        await bot.send_message(user_id, """<b>Выберете действие:</b>""", parse_mode="HTML", reply_markup=await subMain_kb())
    elif user_text == "Н" or user_text == "н" or user_text == "N" or user_text == "n":
        await state.finish()
        await bot.send_message(user_id, """Прервано.""", parse_mode="HTML", reply_markup=await subMain_kb())
        await bot.send_message(user_id, """<b>Выберете действие:</b>""", parse_mode="HTML", reply_markup=await subMain_kb())
    elif user_text == "Stop":
        await state.finish()
        await bot.send_message(user_id, """<b>Выберете действие:</b>""", parse_mode="HTML", reply_markup=await subMain_kb())
    else:
        await state.finish()
        await bot.send_message(user_id, """Прервано.""", parse_mode="HTML", reply_markup=await subMain_kb())
        await bot.send_message(user_id, """<b>Выберете действие:</b>""", parse_mode="HTML")


async def add_requests(user_id, user_sub):
    if user_sub == "mini":
        await set_requests(user_id, 100, 10, 5)
    if user_sub == "starter":
        await set_requests(user_id, -1, 30, 25)
    if user_sub == "premium":
        await set_requests(user_id, -1, 50, 50)
    if user_sub == "ultra":
        await set_requests(user_id, -1, 100, 100)
    if user_sub == "maximum":
        await set_requests(user_id, -1, -1, -1)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
