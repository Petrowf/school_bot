from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, message
from dotenv import load_dotenv
import os

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot)

main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add('Расписание').add('Новости').add('Оценки')

main_admin = ReplyKeyboardMarkup(resize_keyboard=True)
main_admin.add('Расписание').add('Новости').add('Оценки').add("Админ-панель")

admin_panel = ReplyKeyboardMarkup(resize_keyboard=True)
admin_panel.add('Добавить расписание').add('Добавить новость').add('Добавить оценки').add("Админ-панель")


@dp.message_handler(commands=["start"])
async def cmd_srart(message: types.Message):
    await message.answer_sticker('CAACAgIAAxkBAAMUZWGdovgTgW-qmp7noVjZrrRF2Y0AAgUAA8A2TxP5al-agmtNdTME')
    await message.answer(f"{message.from_user.first_name}, добро пожаловать в школьный бот",
                         reply_markup=main)
    if message.from_user.id == os.getenv('ADMIN_ID'):
        await message.answer(f'Вы авторизовались', reply_markup=main_admin)


@dp.message_handler(commands=["id"])
async def cmd_id(message: types.Message):
    await message.answer(f"{message.from_user.id}")


@dp.message_handler(text='Расписание')
async def contacts(message: types.Message):
    await message.answer(
        f'Пока расписания нету')  # ЗДЕСЬ НУЖНО НАПИСАТЬ, ЧТО ДЕЛАЕТ БОТ, ЕСЛИ НАПИСАТЬ ЕМУ 'РАСПИСАНИЕ', ПОДОБНОЕ СДЕЛАТЬ И С ОЦЕНКАМИ И ДРУГИМИ КНОПКАМИ


@dp.message_handler(text='Админ-панель')
async def contacts(message: types.Message):
    await message.answer(f'Вы вошли в админ панель', reply_markup=admin_panel)


@dp.message_handler(content_types=["sticker"])
async def check_sticker(message: types.Message):
    await message.answer(message.sticker.file_id)
    await bot.send_message(message.from_user.id, str(message.chat.id))


@dp.message_handler(content_types=["document", "foto"])
async def forward_message(message: types.Message):
    await bot.forward_message(os.getenv('GROUP_ID'), message.from_user.id, message.message_id)


@dp.message_handler()
async def anwser(message: types.Message):
    await message.reply("я тебя не понимаю")


if __name__ == "__main__":
    dp.start_polling()
