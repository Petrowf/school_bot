import openai
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os
import sqlite3 as sq

load_dotenv()
openai.api_key = os.getenv('OPENAI')
openai.api_base = "http://localhost:1337/v1"
bot = Bot(os.getenv('TOKEN'))
group_id = os.getenv('GROUP_ID')
dp = Dispatcher(bot=bot, storage=MemoryStorage())
main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add('Расписание').add('Новости').add('Оценки')
con = sq.connect('users.db')
cur = con.cursor()


class BotState(StatesGroup):
    news_text = State()
    news_choice = State()
    ttb_wait = State()


admin_panel = InlineKeyboardMarkup(row_width=2)
admin_panel.add(InlineKeyboardButton("Поменять расписание", callback_data="tmtb_change"),
                InlineKeyboardButton("Опубликовать новость", callback_data="nws_change"))


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    global cur
    query = f'SELECT user_name FROM users WHERE id={message.from_user.id}'
    cur.execute(query)
    user_name = cur.fetchone()
    surname = message.from_user.last_name
    name = message.from_user.first_name
    chat_id = message.chat.id
    id = message.from_user.id
    access = 'common'  # common - это пользователь без прав
    if user_name is None:
        new_user_name = message.from_user.username
        query = 'INSERT INTO users (id, user_name, chat_id, name, surname, access) VALUES (?, ?, ?, ?, ?, ?);'
        cur.execute(query, (id, new_user_name, chat_id, name, surname, access))
        con.commit()
    await message.answer_sticker('CAACAgIAAxkBAAMUZWGdovgTgW-qmp7noVjZrrRF2Y0AAgUAA8A2TxP5al-agmtNdTME')
    await message.answer(f"{message.from_user.first_name}, добро пожаловать в школьный бот",
                         reply_markup=main)
    if str(message.chat.id) in os.getenv('ADMIN_ID'):
        await message.answer(f'Вы авторизовались.', reply_markup=admin_panel)


@dp.callback_query_handler(text="tmtb_change")
async def wait_photo(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.message.chat.id, "Отправьте фото расписания")
    await state.set_state(BotState.ttb_wait.state)
    print("Work!")


@dp.message_handler(commands=["id"])
async def cmd_id(message: types.Message):
    await message.answer(f"{message.chat.id}")


@dp.message_handler(text='Расписание')
async def contacts(message: types.Message):
    photo = InputFile("time_table/ttable.png")
    await message.answer("Вот расписание:")
    await message.answer_photo(photo)


@dp.callback_query_handler(text="admin-ui")
async def contacts(message: types.Message):
    await message.answer(f'Вы вошли в админ панель', reply_markup=admin_panel)


@dp.message_handler(content_types=["sticker"])
async def check_sticker(message: types.Message):
    await message.answer(message.sticker.file_id)
    await bot.send_message(message.from_user.id, str(message.chat.id))


async def ttb_save(message, state: FSMContext):
    await message.photo[-1].download('./time_table/ttable.png')
    await message.answer("Расписание успешно изменено!")
    await state.finish()


@dp.callback_query_handler(text="nws_change")
async def ask_for_news(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.message.chat.id, "Введите текст новости:")
    # Сохраняем текст новости в контексте пользователя
    await state.set_state(BotState.news_text.state)


async def edit_news(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        edited_news_text = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": """Ты - редактор публикаций. Ты должен отвечать только 
            отредактированным текстом. Нельзя спрашивать о чём-либо и давать варианты. ТОЛЬКО отредактированный текст.
            Даже без фраз на подобии "Вот, что у меня получилось."."""}
                , {"role": "user", "content": "Отредактируй эту публикацию: " + message.text}],
            stream=False,
        ).choices[0].message.content
        data["news_text"] = message.text
        data["edited_news_text"] = edited_news_text
        await bot.send_message(message.chat.id, f"Отредактированный текст: {edited_news_text}")

        await message.answer("Выберите текст новости:", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Введенный текст", callback_data="original")],
                [InlineKeyboardButton(text="Отредактированный текст", callback_data="edited")],
            ]
        ))
        await state.set_state(BotState.news_choice.state)


async def send_news(callback: types.CallbackQuery, state: FSMContext):
    # Получаем выбранный пользователем текст новости из контекста пользователя
    data = await state.get_data()
    if callback.data == "original":
        news_text = data["news_text"]
    else:
        news_text = data["edited_news_text"]
    # Публикуем новость в группе
    await bot.send_message(group_id, news_text)
    print("Работает!")
    # Сбрасываем состояние пользователя
    await state.finish()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(edit_news, state=BotState.news_text)
    dp.register_callback_query_handler(send_news, state=BotState.news_choice)
    dp.register_message_handler(ttb_save, state=BotState.ttb_wait, content_types=["photo"])


if __name__ == "__main__":
    register_handlers(dp)
    executor.start_polling(dp)
