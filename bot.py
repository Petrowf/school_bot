# Импорт необходимых библиотек
import asyncio
import os
import sqlite3 as sq
import time
import anthropic
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, InputFile, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from dotenv import load_dotenv
# Загрузка переменных окружения из .env файла
load_dotenv()

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.getenv('CLAUDE'),
)
bot = Bot(os.getenv('TOKEN'))
group_id = os.getenv('GROUP_ID')

# Инициализация диспетчера с хранилищем состояний
dp = Dispatcher(bot=bot, storage=MemoryStorage())
cancel_up = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True).add("Отмена")
# Создание клавиатур для взаимодействия с ботом
main = InlineKeyboardMarkup(row_width=1)
main.add(InlineKeyboardButton("Расписание", callback_data="ttb"),
         InlineKeyboardButton("Информация о сотруднике", callback_data="wrkr_get"))
topics_s = ReplyKeyboardMarkup(resize_keyboard=True)
tlib = {'Городские новости': 4,
        'Новости гимназии': 2, "Беркут": 6,
        "Движение первых": 68, "OCTOPUS": 3}
for key in tlib:
    topics_s.add(key)

# Соединение с базами данных
con = sq.connect('users.db')
cur = con.cursor()
wcon = sq.connect('workers.db')
wcur = wcon.cursor()
evcn = sq.connect('events.db')
evcur = wcon.cursor()


# Определение состояний для FSM
class BotState(StatesGroup):
    news_text = State()
    news_choice = State()
    ttb_wait = State()
    role_wait = State()
    un_wait = State()
    report_wait = State()
    wrkr_wait = State()
    gwrkr_wait = State()
    ev_wait = State()
    tnum_wait = State()


# Создание панелей администратора и других ролей
admin_panel = InlineKeyboardMarkup(row_width=2)
admin_panel.add(InlineKeyboardButton("Поменять расписание", callback_data="tmtb_change"),
                InlineKeyboardButton("Опубликовать новость", callback_data="nws_change"),
                InlineKeyboardButton("Поменять роль", callback_data="role_change"),
                InlineKeyboardButton("Отправить замечание разработчикам", callback_data="report"),
                InlineKeyboardButton("Добавить сотрудника", callback_data="wrkr_add"),
                InlineKeyboardButton("Информация о сотруднике", callback_data="wrkr_get"))

planner_panel = InlineKeyboardMarkup()
planner_panel.add(InlineKeyboardButton("Поменять расписание", callback_data="tmtb_change"),
                  InlineKeyboardButton("Информация о сотруднике", callback_data="wrkr_get"))
zvr_panel = InlineKeyboardMarkup()
zvr_panel.add(InlineKeyboardButton("Поменять расписание", callback_data="tmtb_change"),
              InlineKeyboardButton("Информация о сотруднике", callback_data="wrkr_get"))
role_panel = ReplyKeyboardMarkup()
role_panel.add('Школьник/Сотрудник').add('Администратор').add('Планировщик').add('Редактор новостей').add("Отмена")


@dp.message_handler(commands=["help"])
async def instructions(message: types.Message):
    query = f'SELECT access FROM users WHERE id={message.from_user.id}'
    cur.execute(query)
    if cur.fetchone()[0] == 'admin':
        await message.answer("""Поменять расписание:
\tВы должны отправить фото актуального расписания
Опубликовать новость:
\t1 шаг: Отправьте боту текст новости
\t2 шаг: Выберите какой текст отправлять: исходный, отредактированный или отменить отправку
\t3 шаг: Если вы всё-таки выбрали отправить сообщение, то выберете группу для отправки 
Поменять роль:
\t1 шаг: выберете новую роль для человека
\t2 шаг: напишите его tg username (по @)
Отправить замечание разработчикам:
	Напишите замечание 
Добавить сотрудника:
	Напишите информацию о сотруднике в сообщенной ботом форме
Расписание
	Бот отправит вам фото актуального расписания
Информация о сотруднике:
	Напишите ФИО, а бот вам о нем расскажет
""")

    if cur.fetchone()[0] == 'common':
        await message.answer("""Кнопки

Расписание: Бот отправит вам фото актуального расписания
Информация о сотруднике: Напишите ФИО, а бот вам о нем расскажет

""")


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message, state: FSMContext):
    try:
        query = f'SELECT user_name, access FROM users WHERE id={message.from_user.id}'
        cur.execute(query)
        user_name, role = cur.fetchone()
    except:
        user_name, role = None, None
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
    await message.answer(
        f"{message.from_user.first_name}, добро пожаловать в школьный бот. "
        f"Я буду публиковать новости здесь: https://t.me/+bph2-lwMswpmNGJi."
        f" \nХочешь узнать, что я умею? Напиши /help",
        reply_markup=main)
    if role == 'admin':
        await message.answer(f'Здравствуйте администратор!', reply_markup=admin_panel)
    elif role == 'planner':
        await message.answer(f'Здравствуйте Планировщик расписаний!', reply_markup=planner_panel)
    elif role == 'zvr':
        await message.answer(f'Здравствуйте Зам. по воспитательной работе!', reply_markup=planner_panel)


@dp.callback_query_handler(text="wrkr_add")
async def wait_worker(callback: types.CallbackQuery, state: FSMContext):
    query = f'SELECT access FROM users WHERE id={callback.from_user.id}'
    cur.execute(query)
    if cur.fetchone()[0] == 'admin':
        await bot.send_message(callback.message.chat.id, """Напишите информацию о сотруднике с фото в указанной форме:\n
ФИО\nТелефон\nДолжность\nКарьера\nОпыт(в годах)\nПочта""", reply_markup=cancel_up)
        await state.set_state(BotState.wrkr_wait.state)

    else:
        await bot.send_message(callback.message.chat.id, "У вас нет полномочий для добавления сотрудника")


@dp.callback_query_handler(text="wrkr_get")
async def wait_eworker(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.message.chat.id, """Напишите информацию о сотруднике в указанной форме:
Ф И О сотрудника""")
    await state.set_state(BotState.gwrkr_wait.state)


@dp.callback_query_handler(text="ae")
async def wait_worker(callback: types.CallbackQuery, state: FSMContext):
    query = f'SELECT access FROM users WHERE id={callback.from_user.id}'
    cur.execute(query)
    if cur.fetchone()[0] == 'admin':
        await bot.send_message(callback.message.chat.id, """Напишите информацию о мероприятии таким форматом:
        Название
        Дата начала
        Дата конца
        Организатор
        Телеграмм тэг""")
        await state.set_state(BotState.ev_wait.state)

    else:
        await bot.send_message(callback.message.chat.id, "У вас нет полномочий для добавления мероприятия")


@dp.message_handler(state=BotState.ev_wait)
async def wrkr_get(message: types.Message, state: FSMContext):
    wrkr_i = list(message.caption.split("\n"))
    query = 'INSERT INTO workers ( name, time_start, time_end, contact_person, tg_teg) VALUES ' \
            '(?,?,?,?,?);'
    evcur.execute(query, (wrkr_i[0], wrkr_i[1], wrkr_i[2], wrkr_i[3], wrkr_i[4]))
    evcn.commit()
    await message.answer(f"Мероприятие успешно добавлено")
    await state.finish()


@dp.callback_query_handler(text="tmtb_change")
async def wait_photo(callback: types.CallbackQuery, state: FSMContext):
    query = f'SELECT access FROM users WHERE id={callback.from_user.id}'
    cur.execute(query)
    if cur.fetchone()[0] == 'admin' or cur.fetchone()[0] == 'planner':
        await bot.send_message(callback.message.chat.id, "Отправьте фото расписания")
        await state.set_state(BotState.ttb_wait.state)
    else:
        await bot.send_message(callback.message.chat.id, "У вас нет полномочий для редактирования расписания")


@dp.callback_query_handler(text="report")
async def get_report(callback: types.CallbackQuery, state: FSMContext):
    query = f'SELECT access FROM users WHERE id={callback.from_user.id}'
    cur.execute(query)
    if cur.fetchone()[0] == 'admin':
        await bot.send_message(callback.message.chat.id, "Отправьте описание жалобы", reply_markup=cancel_up)
        await state.set_state(BotState.report_wait.state)
    else:
        await bot.send_message(callback.message.chat.id, "У вас нет полномочий для отправки жалобы")


@dp.callback_query_handler(text="role_change")
async def wait_role(callback: types.CallbackQuery, state: FSMContext):
    query = f'SELECT access FROM users WHERE id={callback.from_user.id}'
    cur.execute(query)

    if cur.fetchone()[0] == 'admin':
        await bot.send_message(callback.message.chat.id, "Выберите роль пользователя", reply_markup=role_panel)
        await state.set_state(BotState.role_wait.state)
    else:
        await bot.send_message(callback.message.chat.id, "У вас нет полномочий для изменения роли пользователя")


@dp.message_handler(commands=["id"])
async def cmd_id(message: types.Message):
    await message.answer(f"{message.chat.id}")


@dp.message_handler(state=BotState.role_wait)
async def role_set(message: types.Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.finish()
        ch = await bot.send_message(message.chat.id, "Отменено!", reply_markup=types.ReplyKeyboardRemove())
        time.sleep(0.5)
        await ch.delete()
        await bot.send_message(message.chat.id, "Панель", reply_markup=admin_panel)
        await state.finish()
    else:
        async with state.proxy() as data:
            if message.text == 'Школьник/Сотрудник':
                await message.answer("Теперь напишите username пользователя (по @)")
                data["role"] = "commonn"
                await state.finish()
                await state.set_state(BotState.un_wait.state)
            elif message.text == 'Администратор':
                await message.answer("Теперь напишите username пользователя (по @)")
                data["role"] = "admin"
                await state.finish()
                await state.set_state(BotState.un_wait.state)
            elif message.text == 'Редактор новостей':
                data["role"] = "zvr"
                await state.finish()
                await message.answer("Теперь напишите username пользователя (по @)")
                await state.set_state(BotState.un_wait.state)
            elif message.text == 'Планировщик':
                await message.answer("Теперь напишите username пользователя (по @)")
                data["role"] = "planner"
                await state.finish()
                await state.set_state(BotState.un_wait.state)
            else:
                await message.answer("Задана неправильная роль. Попробуйте ещё раз", reply_markup=admin_panel)
                await state.finish()


@dp.message_handler(state=BotState.un_wait)
async def role_change(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        query = f"UPDATE users SET access = ? WHERE user_name = ?"
        cur.execute(query, (data["role"], message.text))
        con.commit()
        await message.answer("Роль успешно изменена!")
    except Exception as e:
        await message.answer("Задан неправильный username. Попробуйте ещё раз", reply_markup=admin_panel)
    await state.finish()


@dp.message_handler(state=BotState.wrkr_wait, content_types=["text", 'photo'])
async def wrkr_add(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.reply("Отправьте анкету с фотографией")
    else:
        wrkr_i = list(message.caption.split("\n"))
        if not "@" in wrkr_i[-1] or not "." in wrkr_i[-1]:
            await message.answer(f"Неправильная почта, попробуйте ещё раз")

        else:
            wrkr_i[0:1] = (wrkr_i[0].split(" "))
            wrkr_i[6] = int(wrkr_i[6])
            tkn = message.photo[-1].file_id
            path = f'./wrkrs/{tkn}'
            wrkr_i += [path]
            await message.photo[-1].download(path)
            query = 'INSERT INTO workers (' \
                    'last_name, name, surname, phone, work, education, experience, email, photo) VALUES ' \
                    '(?, ?, ' \
                    '?, ' \
                    '?, ?, ?, ?, ?, ?);'
            wcur.execute(query, wrkr_i)
            wcon.commit()
            query = f'SELECT id FROM workers WHERE phone={wrkr_i[3]}'
            wcur.execute(query)
            await message.answer(f"Сотрудник успешно добавлен")
            await state.finish()


@dp.message_handler(commands=['clean'])
async def cmd_clear(message: types.Message):
    try:
        # Все сообщения, начиная с текущего и до первого (message_id = 0)
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, i)
    except:
        await bot.send_message(message.chat.id, "Всё удалено!")


@dp.message_handler(state=BotState.gwrkr_wait)
async def wrkr_get(message: types.Message, state: FSMContext):
    query = f'SELECT name, surname, last_name,phone, work, education, experience, email, photo FROM workers WHERE ' \
            f'(last_name, name, surname) = (?, ?, ?)'
    try:
        wcur.execute(query, tuple(message.text.split()))
        name, surname, last_name, phone, work, education, experience, email, photo = wcur.fetchone()
        photo = InputFile(photo)

        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=f" ФИО: {last_name} {name} {surname}"
                                                                           f"\nТелефон: {phone}"
                                                                           f", \nДолжность: {work}, "
                                                                           f"\nКарьера: {education}, \nОпыт: {experience}"
                                                                           f" (в годах), "
                                                                           f"\nПочта: {email}")

    except:
        bmsg = await message.answer("Данного сотрудника нет в базе данных")
        time.sleep(2.5)
        await bmsg.delete()
        await message.answer("Панель", reply_markup=main)
        await message.delete()

    await state.finish()


@dp.message_handler(state=BotState.report_wait)
async def report(message: types.Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.finish()
        ch = await bot.send_message(message.chat.id, "Отменено!", reply_markup=types.ReplyKeyboardRemove())
        time.sleep(0.5)
        await ch.delete()
        await bot.send_message(message.chat.id, "Панель", reply_markup=admin_panel)
    else:
        await bot.send_message(1109823137, "Вам отправлена жалоба: " + message.text)
    await state.finish()


@dp.callback_query_handler(text="ttb")
async def time_table(callback: types.CallbackQuery):
    photo = InputFile("time_table/ttable.png")
    await bot.send_photo(callback.message.chat.id, photo=photo, caption="Расписание:")


async def ttb_save(message, state: FSMContext):
    await message.photo[-1].download('./time_table/ttable.png')
    await message.answer("Расписание успешно изменено!")
    await state.finish()


@dp.callback_query_handler(text="nws_change")
async def ask_for_news(callback: types.CallbackQuery, state: FSMContext):
    query = f'SELECT access FROM users WHERE id={callback.from_user.id}'
    cur.execute(query)

    if cur.fetchone()[0] == 'admin' or cur.fetchone()[0] == 'zvr':
        await bot.send_message(callback.message.chat.id, "Отправьте новость (не более 1 фото):", reply_markup=cancel_up)
        # Сохраняем текст новости в контексте пользователя
        await state.set_state(BotState.news_text.state)
    else:
        await bot.send_message(callback.message.chat.id, "У вас нет полномочий для публикации новостей")


async def edit_news(message: types.Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.finish()
        ch = await bot.send_message(message.chat.id, "Отменено!", reply_markup=types.ReplyKeyboardRemove())
        time.sleep(0.5)
        await ch.delete()
        await state.finish()
        await bot.send_message(message.chat.id, "Панель", reply_markup=admin_panel)
    else:
        async with state.proxy() as data:
            if message.photo:
                data["photo"] = message.photo[-1].file_id
                text = message.caption
            else:
                data["photo"] = None
                text = message.text
            edited_news_text = client.messages.create(
                model="claude-3-haiku-20240307",
                messages=[
                    {"role": "user", "content": """Ты - редактор публикаций. 
                    Ты должен отвечать только развёрнутым отредактированным грамотным текстом.
                     Нельзя спрашивать о чём-либо и давать варианты.
                      ТОЛЬКО отредактированный текст.
                       Не используя фраз на подобии "Вот, что у меня получилось."."""},
                    {"role": "assistant", "content": "Хорошо, я постараюсь"},
                    {"role": "user", "content": "Отредактируй эту публикацию: " + text}
                ],
                max_tokens=2048
            ).content[0].text
            data["news_text"] = text
            data["edited_news_text"] = edited_news_text

        await bot.send_message(message.chat.id, f"Отредактированный текст: {edited_news_text}")
        await message.answer("Выберите текст новости:", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Введенный текст", callback_data="original")],
                [InlineKeyboardButton(text="Отредактированный текст", callback_data="edited")],
                [InlineKeyboardButton(text="Отменить", callback_data="cancel")],
            ]
        ))
        await state.set_state(BotState.news_choice.state)


async def send_news(message: types.Message, state: FSMContext):
    # Получаем выбранный пользователем текст новости из контекста пользователя
    try:
        _ = tlib[message.text]
        textmess = await state.get_data()
        news_text = textmess["text"]
        if textmess["photo"]:
            await bot.send_photo(group_id, caption=news_text, message_thread_id=tlib[message.text],
                                 photo=textmess['photo'])
        else:
            await bot.send_message(group_id, news_text, message_thread_id=tlib[message.text])

        await message.reply("Успешно отправлено!", reply_markup=types.ReplyKeyboardRemove())
        await bot.send_message(message.chat.id, "Панель", reply_markup=admin_panel)
    except:
        ch = await message.reply("Неверный канал", reply_markup=types.ReplyKeyboardRemove())
        time.sleep(0.5)
        await ch.delete()
        await message.delete()
        await bot.send_message(message.chat.id, "Панель", reply_markup=admin_panel)

    async with state.proxy() as data:
        await data['msg_to_delete'].delete()
        await state.finish()


async def req_news(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        d = await state.get_data()
        if callback.data == "original":
            data["text"] = d["news_text"]
            data['msg_to_delete'] = await bot.send_message(
                callback.message.chat.id, "Теперь выберите канал для отправки", reply_markup=topics_s)
            # Сбрасываем состояние пользователя
            await state.set_state(BotState.tnum_wait.state)
        elif callback.data == "cancel":
            await state.finish()
            await bot.send_message(callback.message.chat.id, "Отменено!")
            await bot.send_message(callback.message.chat.id, "Панель", reply_markup=admin_panel)
        else:
            data["text"] = d["edited_news_text"]
            data['msg_to_delete'] = await bot.send_message(
                callback.message.chat.id, "Теперь выберите канал для отправки", reply_markup=topics_s)
            # Сбрасываем состояние пользователя
            await state.set_state(BotState.tnum_wait.state)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(edit_news, state=BotState.news_text, content_types=["text", "photo", "video"])
    dp.register_message_handler(send_news, state=BotState.tnum_wait)
    dp.register_callback_query_handler(req_news, state=BotState.news_choice)
    dp.register_message_handler(ttb_save, state=BotState.ttb_wait, content_types=["photo"])


if __name__ == "__main__":
    register_handlers(dp)
    executor.start_polling(dp, skip_updates=True)
