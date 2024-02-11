import os
import sqlite3 as sq
import time
from pathlib import Path
import gdown
import openai
import pandas as pd
import wget
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('SHUTTLE')
openai.api_base = "https://api.shuttleai.app/v1"
bot = Bot(os.getenv('TOKEN'))
group_id = os.getenv('GROUP_ID')
dp = Dispatcher(bot=bot, storage=MemoryStorage())
main = InlineKeyboardMarkup(row_width=1)
main.add(InlineKeyboardButton("Расписание", callback_data="ttb"),
         InlineKeyboardButton("Информация о сотруднике", callback_data="wrkr_get"))
topics_s = ReplyKeyboardMarkup(resize_keyboard=True)
tlib = {'Министерство Образования | Красноярский край': 4, 'Новости гимназии': 2, "Беркут": 8, "РДДМ": 6, "OCTOPUS": 3}
for key in tlib:
    topics_s.add(key)
con = sq.connect('users.db')
cur = con.cursor()
wcon = sq.connect('workers.db')
wcur = wcon.cursor()

evcn = sq.connect('events.db')
evcur = wcon.cursor()


class BotState(StatesGroup):
    news_text = State()
    news_choice = State()
    ttb_wait = State()
    role_wait = State()
    un_wait = State()
    ttbch_wait = State()
    report_wait = State()
    wrkr_wait = State()
    gwrkr_wait = State()
    ev_wait = State()
    tnum_wait = State()


admin_panel = InlineKeyboardMarkup(row_width=2)
admin_panel.add(InlineKeyboardButton("Поменять расписание", callback_data="tmtb_change"),
                InlineKeyboardButton("Опубликовать новость", callback_data="nws_change"),
                # InlineKeyboardButton("Мероприятия", callback_data="ev_get"),
                # InlineKeyboardButton("Опубликовать мероприятие", callback_data="ev_create"),
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
role_panel.add('Школьник/Сотрудник').add('Администратор').add('Планировщик').add('Редактор новостей')


def get_subjects_and_times_by_class(class_name):
    df = pd.read_excel('./time_table/ttable.xlsx', engine='openpyxl', header=None)
    # Find the rows where the class name appears
    class_rows = df[df[0].str.contains(class_name, na=False)].index

    # Extract the subjects and times for the class
    class_schedule = []
    for row in class_rows:
        next_row = row + 1
        while next_row < len(df) and not df.iloc[next_row][0].startswith('Класс'):
            subject_time = df.iloc[next_row][0].split(' - ')
            class_schedule.append({
                'Урок': subject_time[0],
                'Время': subject_time[1]
            })
            next_row += 1

    # Convert the list of dictionaries to a DataFrame
    class_schedule_df = pd.DataFrame(class_schedule)
    return class_schedule_df


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
    await message.answer(f"{message.from_user.first_name}, добро пожаловать в школьный бот",
                         reply_markup=main)
    if role == 'admin':
        await state.update_data(urole="admin")
        await message.answer(f'Здравствуйте администратор!', reply_markup=admin_panel)
    elif role == 'planner':
        await state.update_data(urole="planner")
        await message.answer(f'Здравствуйте планировщик расписаний!', reply_markup=planner_panel)
    elif role == 'zvr':
        await state.update_data(urole="zvr")
        await message.answer(f'Здравствуйте Зам. по воспитательной работе!', reply_markup=planner_panel)


@dp.callback_query_handler(text="wrkr_add")
async def wait_worker(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data['urole'] == 'admin':
        await bot.send_message(callback.message.chat.id, """Напишите информацию о сотруднике с фото в указанной форме:
Имя\nФамилия\nОтчество\nТелефон\nДолжность\nКарьера\nОпыт(в годах)\nПочта""")
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
    async with state.proxy() as data:
        if data['urole'] == 'admin':
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
async def wrkr_add(message: types.Message, state: FSMContext):
    wrkr_i = list(message.caption.split("\n"))
    query = 'INSERT INTO workers ( name, time_start, time_end, contact_person, tg_teg) VALUES ' \
            '(?,?,?,?,?);'
    evcur.execute(query, (wrkr_i[0], wrkr_i[1], wrkr_i[2], wrkr_i[3], wrkr_i[4]))
    evcn.commit()
    await message.answer(f"Мероприятие успешно добавлено")
    await state.finish()


@dp.callback_query_handler(text="tmtb_change")
async def wait_photo(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data['urole'] == 'admin' or data['urole'] == 'planner':
            await bot.send_message(callback.message.chat.id, "Отправьте ссылку на таблицу расписания в Google Диск")
            await state.set_state(BotState.ttb_wait.state)
        else:
            await bot.send_message(callback.message.chat.id, "У вас нет полномочий для редактирования расписания")


@dp.callback_query_handler(text="report")
async def get_report(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data['urole'] == 'admin':
            await bot.send_message(callback.message.chat.id, "Отправьте описание жалобы")
            await state.set_state(BotState.report_wait.state)
        else:
            await bot.send_message(callback.message.chat.id, "У вас нет полномочий для отправки жалобы")


@dp.callback_query_handler(text="role_change")
async def wait_role(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data['urole'] == 'admin':
            await bot.send_message(callback.message.chat.id, "Выберите роль пользователя", reply_markup=role_panel)
            await state.set_state(BotState.role_wait.state)
        else:
            await bot.send_message(callback.message.chat.id, "У вас нет полномочий для изменения роли пользователя")


@dp.callback_query_handler(text="ge")
async def get_events(callback: types.CallbackQuery):
    query = f'SELECT * from events'
    cur.execute(query)
    mp = cur.fetchall()
    print("Всего строк:  ", len(mp))
    print("Вывод каждой строки")
    text = ""
    for row in mp:
        text += "\nНазвание:", row[0]
        text += "\nНачало:", row[1]
        text += "\nКонец:", row[2]
        text += "\nОрганизатор:", row[3]
        text += "\nТег в Телеграмме:", row[4], "\n\n"
    await bot.send_message(callback.id, "Мероприятие")


@dp.callback_query_handler(text="ge")
async def add_event(callback: types.CallbackQuery):
    query = f'SELECT * from events'
    cur.execute(query)
    mp = cur.fetchall()
    print("Всего строк:  ", len(mp))
    print("Вывод каждой строки")
    text = ""
    for row in mp:
        text += "\nНазвание:", row[0]
        text += "\nНачало:", row[1]
        text += "\nКонец:", row[2]
        text += "\nОрганизатор:", row[3]
        text += "\nТег в Телеграмме:", row[4], "\n\n"
    await bot.send_message(callback.id, "Мероприятие")


@dp.message_handler(commands=["id"])
async def cmd_id(message: types.Message):
    await message.answer(f"{message.chat.id}")


@dp.message_handler(state=BotState.role_wait)
async def role_set(message: types.Message, state: FSMContext):
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


@dp.message_handler(state=BotState.wrkr_wait, content_types=['photo'])
async def wrkr_add(message: types.Message, state: FSMContext):
    wrkr_i = list(message.caption.split("\n"))
    if not "@" in wrkr_i[-1] or not "." in wrkr_i[-1]:
        await message.answer(f"Неправильная почта, попробуйте ещё раз")
    else:
        wrkr_i[6] = int(wrkr_i[6])
        tkn = message.photo[-1].file_id
        path = f'./wrkrs/{tkn}'
        wrkr_i += [path]
        await message.photo[-1].download(path)
        query = 'INSERT INTO workers ( name, surname, last_name, ' \
                'phone, work, education, experience, email, photo) VALUES ' \
                '(?, ?, ' \
                '?, ' \
                '?, ?, ?, ?, ?, ?);'
        wcur.execute(query, wrkr_i)
        wcon.commit()
        query = f'SELECT id FROM workers WHERE phone={wrkr_i[3]}'
        wcur.execute(query)
        await message.answer(f"Сотрудник успешно добавлен")
        await state.finish()


@dp.message_handler(state=BotState.gwrkr_wait)
async def wrkr_get(message: types.Message, state: FSMContext):
    query = f'SELECT name, surname, last_name, phone, work, education, experience, email, photo FROM workers WHERE ' \
            f'(surname, name, last_name) = (?, ?, ?)'
    try:
        wcur.execute(query, tuple(message.text.split()))
        name, surname, last_name, phone, work, education, experience, email, photo = wcur.fetchone()
        photo = InputFile(photo)

        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=f" ФИО: {surname} {name} {last_name}"
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
async def role_change(message: types.Message, state: FSMContext):
    await bot.send_message(1109823137, "Вам отправлена жалоба: " + message.text)
    await state.finish()


@dp.callback_query_handler(text="ttb")
async def ttb_get(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.message.chat.id, "Введите номер и букву класса")
    await state.set_state(BotState.ttbch_wait.state)


@dp.message_handler(state=BotState.ttbch_wait)
async def ttbfn_get(message: types.Message, state: FSMContext):
    if "Время" in str(get_subjects_and_times_by_class(message.text)):
        await message.answer(str(get_subjects_and_times_by_class(message.text)))
    else:
        await message.answer("Таблица не найдена")
    await state.finish()


async def ttb_save(message, state: FSMContext):
    if Path('./time_table/ttable.xlsx').is_file():
        os.remove('./time_table/ttable.xlsx')
    wget.download(message.text + '/export?exportFormat=xlsx', './time_table/ttable.xlsx', bar=None)
    await message.answer("Расписание успешно изменено!")
    await state.finish()


@dp.callback_query_handler(text="nws_change")
async def ask_for_news(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data['urole'] == 'admin' or data['urole'] == 'zvr':
            await bot.send_message(callback.message.chat.id, "Введите текст новости:")
            # Сохраняем текст новости в контексте пользователя
            await state.set_state(BotState.news_text.state)
        else:
            await bot.send_message(callback.message.chat.id, "У вас нет полномочий для публикации новостей")


async def edit_news(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        edited_news_text = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": """Ты - редактор публикаций. Ты должен отвечать только 
            отредактированным текстом. Нельзя спрашивать о чём-либо и давать варианты. ТОЛЬКО отредактированный текст.
            Не используя фраз на подобии "Вот, что у меня получилось."."""}
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
                [InlineKeyboardButton(text="Отменить", callback_data="cancel")],
            ]
        ))
        await state.set_state(BotState.news_choice.state)


async def send_news(message: types.Message, state: FSMContext):
    # Получаем выбранный пользователем текст новости из контекста пользователя
    try:
        _ = tlib[message.text]
        # Сбрасываем состояние пользователя
        da = True
        textmess = await state.get_data()
        print(textmess)
        news_text = textmess["text"]

        # Публикуем новость в группе
        await bot.send_message(group_id, news_text, message_thread_id=tlib[message.text])
        await message.reply("Успешно отправлено!", reply_markup=None)
        await bot.send_message(message.chat.id, "Панель", reply_markup=admin_panel)
    except:
        ch = await message.reply("Неверный канал", reply_markup=None)
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
        print(d)
        if callback.data == "original":
            data["text"] = d["news_text"]
            data['msg_to_delete'] = await bot.send_message(
                callback.message.chat.id,
                "Теперь выберите канал для отправки",
                reply_markup=topics_s)
            # Сбрасываем состояние пользователя
            await state.set_state(BotState.tnum_wait.state)
        elif callback.data == "cancel":
            await state.finish()
            await bot.send_message(callback.message.chat.id, "Отменено!")
            await bot.send_message(callback.message.chat.id, "Панель", reply_markup=admin_panel)
        else:
            data["text"] = d["edited_news_text"]
            data['msg_to_delete'] = await bot.send_message(
                callback.message.chat.id
                , "Теперь выберите канал для отправки",
                reply_markup=topics_s)
            # Сбрасываем состояние пользователя
            await state.set_state(BotState.tnum_wait.state)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(edit_news, state=BotState.news_text)
    dp.register_message_handler(send_news, state=BotState.tnum_wait)
    dp.register_callback_query_handler(req_news, state=BotState.news_choice)
    dp.register_message_handler(ttb_save, state=BotState.ttb_wait)


if __name__ == "__main__":
    register_handlers(dp)
    executor.start_polling(dp, skip_updates=True)
