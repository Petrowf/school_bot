from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, message, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot)
ttb = False
main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add('Расписание').add('Новости').add('Оценки')

main_admin = ReplyKeyboardMarkup(resize_keyboard=True)
main_admin.add('Расписание').add('Новости').add('Оценки').add("Админ-панель")

admin_panel = InlineKeyboardMarkup(row_width=2)
admin_panel.add(InlineKeyboardButton("Поменять расписание", callback_data="tmtb_change"))


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer_sticker('CAACAgIAAxkBAAMUZWGdovgTgW-qmp7noVjZrrRF2Y0AAgUAA8A2TxP5al-agmtNdTME')
    await message.answer(f"{message.from_user.first_name}, добро пожаловать в школьный бот",
                         reply_markup=main)
    if message.from_user.id == os.getenv('ADMIN_ID'):
        await message.answer(f'Вы авторизовались', reply_markup=main_admin)


@dp.callback_query_handler(text="tmtb_change")
async def send_random_value(callback: types.CallbackQuery):
    await bot.send_message(callback.message.chat.id, "Отправьте фото расписания")
    global ttb
    ttb = True




@dp.message_handler(commands=["id"])
async def cmd_id(message: types.Message):
    await message.answer(f"{message.from_user.id}")


@dp.message_handler(text='Расписание')
async def contacts(message: types.Message):
    photo = InputFile("time_table/ttable.png")
    await message.answer("Вот расписание:")
    await message.answer_photo(photo)


@dp.message_handler(text='Админ-панель')
async def contacts(message: types.Message):
    await message.answer(f'Вы вошли в админ панель', reply_markup=admin_panel)


@dp.message_handler(content_types=["sticker"])
async def check_sticker(message: types.Message):
    await message.answer(message.sticker.file_id)
    await bot.send_message(message.from_user.id, str(message.chat.id))


@dp.message_handler(content_types=["photo"])
async def forward_message(message: types.Message):
    if ttb:
        await message.photo[-1].download('./time_table/ttable.png')


@dp.message_handler()
async def anwser(message: types.Message):
    await message.reply("я тебя не понимаю")


if __name__ == "__main__":
    executor.start_polling(dp)
