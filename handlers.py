from html import escape
from datetime import date, timedelta
from aiogram import Router, types, F
from aiogram.filters import Command

from scripts import (
    load_schedule, current_parity, render_schedule,
    WEEK_ORDER, PARITY_RU, DAY_NAMES_RU, current_day_key
)

router = Router()


#Клава, прилипающая к сообщению
kb = [
        [types.InlineKeyboardButton(text="Текущий день", callback_data='this_day'),
         types.InlineKeyboardButton(text="Текущая неделя", callback_data='this_week')],
        [types.InlineKeyboardButton(text="Неделя числитель", callback_data='num'),
         types.InlineKeyboardButton(text="Неделя знаменатель", callback_data='banner')],
        [types.InlineKeyboardButton(text="Расписание на завтра", callback_data='tomorrow')]
    ]

#Клава для возвращения в меню для остальных сообщ
keyb = [[types.InlineKeyboardButton(text="Меню", callback_data='menu')]]


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyb)
    await message.answer("👋 <b>Добро пожаловать в бот-расписание!</b>\n\n"
        "Выбирай, что показать:\n"
        "📅 <i>Текущий день</i> — пары на сегодня\n"
        "🗓 <i>Текущая неделя</i> — вся текущая неделя\n"
        "🔢 <i>Неделя числитель / знаменатель</i> — конкретная неделя\n\n"
        "👉 Начни с кнопки <b>«Меню»</b>.\n"
        "💌Update: появилась функция просмотра расписания на завтра!", reply_markup=keyboard)


@router.callback_query(F.data.in_({"this_day", "tomorrow"}))
async def day_callback(callback: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyb)

    is_tomorrow = callback.data == "tomorrow"
    target_date = date.today() + timedelta(days=1) if is_tomorrow else date.today()
    prefix = "Завтра" if is_tomorrow else "Сегодня"

    day_key = current_day_key(target_date)
    parity = current_parity(target_date)
    schedule = load_schedule()
    pairs = schedule.get(parity, {}).get(day_key, []) or []

    if not pairs:
        await callback.answer()
        await callback.message.edit_text(
            f"На {prefix.lower()} ({DAY_NAMES_RU[day_key]}, {PARITY_RU[parity]}) пар нет",
            reply_markup=keyboard,
        )
        return

    header = f"📅 <b>{prefix}: {DAY_NAMES_RU[day_key]}</b> · <i>{PARITY_RU[parity]}</i>\n\n"
    lines = []
    for p in pairs:
        lines.append(
            f"🕐 <b>{escape(p['time'])}</b>\n"
            f"📚 {escape(p['subject'])}\n"
            f"🚪 ауд. {escape(p['room'])}   👤 {escape(p['teacher'])}\n"
        )
    body = "\n".join(lines)

    await callback.answer()
    await callback.message.edit_text(header + body, reply_markup=keyboard)


@router.callback_query(F.data == "this_week")
async def about_me_callback(callback: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyb)
    today = date.today()
    parity = current_parity(today)
    schedule = load_schedule()
    text = render_schedule(schedule, parity, WEEK_ORDER)

    await callback.answer()
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "num")
async def about_me_callback(callback: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyb)
    schedule = load_schedule()
    text = render_schedule(schedule, "numerator", WEEK_ORDER)

    await callback.answer()
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "banner")
async def about_me_callback(callback: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyb)
    schedule = load_schedule()
    text = render_schedule(schedule, "denominator", WEEK_ORDER)

    await callback.answer()
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "menu")
async def about_me_callback(callback: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await callback.message.edit_text("Итак-сссс, вот и всё меню перед глазами 👀\n\n"
        "Выбирай, что показать:\n"
        "📅 <i>Текущий день</i> — пары на сегодня\n"
        "🗓 <i>Текущая неделя</i> — вся текущая неделя\n"
        "🔢 <i>Числитель / знаменатель</i> — конкретная неделя\n\n"
        "📖 <i>Расписание на завтра</i> — новая кнопка.", reply_markup=keyboard)


@router.message()
async def echo_handler(message: types.Message) -> None:
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyb)


    await message.answer("🤔 Не распознал ваш текст.\n\n"
        "Пожалуйста, воспользуйтесь кнопками или доступными командами.", reply_markup=keyboard)
