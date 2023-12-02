import openai
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os
import sqlite3 as sq




load_dotenv()
bot = Bot(os.getenv('TOKEN'))
group_id = os.getenv('GROUP_ID')
dp = Dispatcher(bot=bot)
ttb = False
main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add('Расписание').add('Новости').add('Оценки')


class BotState(StatesGroup):
    news_text = State()
    news_choice = State()


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


@dp.message_handler(text='Новости', user_id=os.getenv('ADMIN_ID'))
async def ask_for_news(message: types.Message):
    await message.answer("Введите текст новости:")
    # Сохраняем текст новости в контексте пользователя
    await BotState.news_text.set()


@dp.message_handler(state=BotState.news_text)
async def edit_news(message: types.Message, state: FSMContext):
    # Получаем текст новости из контекста пользователя
    news_text = await state.get_data()
    # Редактируем текст новости с помощью GPT от OpenAI
    edited_news_text = openai.Completion.create(
        engine="davinci",
        prompt=news_text,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    ).choices[0].text
    # Сохраняем отредактированный текст новости в контексте пользователя
    await state.update_data(edited_news_text=edited_news_text)
    # Предлагаем выбрать между введенным и отредактированным текстом новости
    await message.answer("Выберите текст новости:", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Введенный текст", callback_data="original")],
            [InlineKeyboardButton(text="Отредактированный текст", callback_data="edited")],
        ]
    ))
    # Сохраняем состояние пользователя
    await BotState.news_choice.set()


@dp.callback_query_handler(state=BotState.news_choice)
async def send_news(callback: types.CallbackQuery, state: FSMContext):
    # Получаем выбранный пользователем текст новости из контекста пользователя
    data = await state.get_data()
    if callback.data == "original":
        news_text = data["news_text"]
    else:
        news_text = data["edited_news_text"]
    # Публикуем новость в группе
    await bot.send_message(group_id, news_text)
    # Сбрасываем состояние пользователя
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp)


