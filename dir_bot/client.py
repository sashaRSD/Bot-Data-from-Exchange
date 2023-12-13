from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram import types
from dir_bot import create_bot
from dir_base import sqlite_db
from dir_get_data import get
dp = create_bot.dp
bot = create_bot.bot

b_get = ['/Получить_котировки']
b_setup = ['/Настроить_вывод']
contact = ['/Обратная_связь']
donat = ['/Поддержать']
kb_client = ReplyKeyboardMarkup(resize_keyboard=True).add(*b_get).add(*b_setup).add(*contact).insert(*donat)
b_setup = ['Да', 'Нет']
b_setup_cancel = ['/Остановить_настройку']
kb_setup = ReplyKeyboardMarkup(resize_keyboard=True).add(*b_setup).add(*b_setup_cancel)

class FSMClient(StatesGroup):
    id = State()
    stock = State()
    cur = State()
    cryptocur = State()
    username = State()


@dp.message_handler(commands=['start'])
async def commands_start(message: types.Message):
    try:
        await bot.send_message(message.from_user.id, f'Добрый день, {message.from_user.first_name}!', reply_markup=kb_client)
    except:
        await message.delete()
        await message.reply('Напишите мне в личные сообщения')


@dp.message_handler(commands=['Обратная_связь'])
async def commands_contact(message: types.Message):
    await message.answer('Наши контактные данные: \n'
                         'Электронная почта - kaa.1999@mail.ru \n'
                         'Username Telegram - @sasha_rsd')


@dp.message_handler(commands=['set', 'Получить_котировки'])
async def commands_set(message: types.Message):
    text = await get.set_data(message.from_user.id)
    await bot.send_message(message.from_user.id, text)


@dp.message_handler(commands=['setup', 'Настроить_вывод'], state=None)
async def commands_setup(message: types.Message):
    await FSMClient.id.set()
    await bot.send_message(message.from_user.id, "Настройка (1/3)\nВыводить - значение акций?\nОтвет: Да/Нет", reply_markup=kb_setup)


@dp.message_handler(state="*", commands=['Остановить_настройку'])
async def load_stop(message: types.Message, state: FSMContext):
    if await state.get_state() is None:
        return 0
    await state.finish()
    await message.answer('Изменения НЕ сохранены ;)', reply_markup=kb_client)


@dp.message_handler(state=FSMClient.id)
async def load_stock(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да' or message.text.lower() == 'нет':
        async with state.proxy() as data:
            data['id'] = message.from_user.id
        await FSMClient.next()
        async with state.proxy() as data:
            data['stock'] = message.text.lower()
        await FSMClient.next()
        await bot.send_message(message.from_user.id, "Настройка (2/3)\nВыводить - курс валют?\nОтвет: Да/Нет")
    else:
        await bot.send_message(message.from_user.id, "О_о\nЯ не понимаю ваш ответ, попробуйте еще раз\nДа/Нет", reply_markup=kb_setup)


@dp.message_handler(state=FSMClient.cur)
async def load_cur(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да' or message.text.lower() == 'нет':
        async with state.proxy() as data:
            data['cur'] = message.text.lower()
            await FSMClient.next()
        await bot.send_message(message.from_user.id, "Настройка (3/3)\nВыводить - курс криптовалют?\nОтвет: Да/Нет")
    else:
        await bot.send_message(message.from_user.id, "О_о\nЯ не понимаю ваш ответ, попробуйте еще раз\nДа/Нет", reply_markup=kb_setup)


@dp.message_handler(state=FSMClient.cryptocur)
async def load_cryptocur(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да' or message.text.lower() == 'нет':
        async with state.proxy() as data:
            data['cryptocur'] = message.text.lower()
            await FSMClient.next()
            data['username'] = message.from_user.username
            await FSMClient.next()
        await bot.send_message(message.from_user.id, "Записал ;)", reply_markup=kb_client)
        bd_read = await sqlite_db.sql_read(message.from_user.id)
        if bd_read:
            await sqlite_db.sql_delete_command(message.from_user.id)
        await sqlite_db.sql_add_command(state)
        await state.finish()
    else:
        await bot.send_message(message.from_user.id, "О_о\nЯ не понимаю ваш ответ, попробуйте еще раз\nДа/Нет", reply_markup=kb_setup)


@dp.message_handler(commands=['Поддержать'])
async def commands_help(message: types.Message):
    text = 'Жми сюда!'
    url = 'https://www.tinkoff.ru/cf/71ARxuIBdob'
    url_button = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=text, url=url))
    await message.answer('Поддержать автора копейкой ;)', reply_markup=url_button)


@dp.message_handler()
async def commands_help(message: types.Message):
    await bot.send_message(message.from_user.id, get.get_name_moex(message.text), reply_markup=kb_client)
