#!/usr/bin/env python3
"""Demo: автолінзи — дерево каталогу + ○/● + заявка НП → менеджер.

  pip install -r requirements.txt
  copy .env.example .env
  python bot.py
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
import telebot
from telebot import types

from catalog import CATALOG, STOCK_NOTE

ROOT = Path(__file__).resolve().parent
IMAGES = ROOT / "images"

load_dotenv(ROOT / ".env")

TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0") or 0)

if not TOKEN or not ADMIN_CHAT_ID:
    raise SystemExit("Set TELEGRAM_TOKEN and ADMIN_CHAT_ID in .env")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# Telegram не вміє картинки НА кнопках — шлемо графіку над меню (не фото товарів)
IMG_CATEGORY = {
    "Основна оптика": "cat_main.png",
    "ПТФ": "cat_ptf.png",
}
IMG_SUBTYPE = {
    "LED": "led.png",
    "Bi-LED": "biled.png",
    "Лазерні": "laser.png",
    "Ксенон": "xenon.png",
    "LED ПТФ": "ptf_led.png",
    "Ксенон ПТФ": "ptf_xen.png",
}
IMG_MAKER = {
    "Aozoom": "aozoom.png",
    "Sanvi": "sanvi.png",
}

bot.set_my_commands(
    [
        types.BotCommand("start", "Головне меню"),
        types.BotCommand("catalog", "Каталог автолінз"),
        types.BotCommand("order", "Оформити заявку"),
        types.BotCommand("cancel", "Скасувати"),
    ]
)
try:
    bot.set_chat_menu_button(menu_button=types.MenuButtonCommands())
except Exception:
    pass

sessions: dict[int, dict] = {}

BTN_HOME = "🏠 Меню"
BTN_BACK = "⬅️ Назад"
BTN_CANCEL = "❌ Скасувати"

# category → type → manufacturer → car brand → model → year → item
STEPS = ("category", "subtype", "maker", "brand", "model", "year", "item")
PATH_KEYS = ("category", "subtype", "maker", "brand", "model", "year")
ORDER_STEPS = ("first_name", "last_name", "phone", "city", "np")


def reset(uid: int) -> None:
    sessions.pop(uid, None)


def price_txt(item: dict) -> str:
    p = item.get("price")
    if p is None:
        return "ціна після уточнення"
    return f"{p} грн"


def main_kb() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🛍 Каталог")
    kb.row("🚚 Доставка", "📞 Контакти")
    return kb


def input_kb() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(BTN_BACK, BTN_HOME)
    kb.row(BTN_CANCEL)
    return kb


def path_node(st: dict, depth: int):
    node = CATALOG
    for i in range(depth):
        node = node[st[PATH_KEYS[i]]]
    return node


def labels_at(st: dict, step: str) -> list[str]:
    if step == "category":
        return list(CATALOG.keys())
    if step == "item":
        return [i["name"] for i in path_node(st, 6)]
    idx = STEPS.index(step)
    return list(path_node(st, idx).keys())


def btn_label(step: str, name: str) -> str:
    """Emoji on buttons (Telegram can't put real images on button faces)."""
    icons = {
        "category": {
            "Основна оптика": "🔦 Основна оптика",
            "ПТФ": "🌫️ ПТФ",
        },
        "subtype": {
            "LED": "💡 LED",
            "Bi-LED": "💠 Bi-LED",
            "Лазерні": "✨ Лазерні",
            "Ксенон": "🌕 Ксенон",
            "LED ПТФ": "💡 LED ПТФ",
            "Ксенон ПТФ": "🌕 Ксенон ПТФ",
        },
        "maker": {
            "Aozoom": "🔵 Aozoom",
            "Sanvi": "🟢 Sanvi",
        },
    }
    if step in icons and name in icons[step]:
        return icons[step][name]
    if step == "brand":
        return f"🚗 {name}"
    if step == "model":
        return f"📦 {name}"
    if step == "year":
        return f"📅 {name}"
    return name


def nav_row() -> list:
    return [
        types.InlineKeyboardButton("⬅️ Назад", callback_data="p:back"),
        types.InlineKeyboardButton("🏠 Меню", callback_data="p:home"),
    ]


def branch_kb(st: dict, step: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup()
    for i, name in enumerate(labels_at(st, step)):
        kb.add(
            types.InlineKeyboardButton(
                btn_label(step, name), callback_data=f"p:{step}:{i}"
            )
        )
    if step == "category":
        kb.add(types.InlineKeyboardButton("🏠 Меню", callback_data="p:home"))
    else:
        kb.row(*nav_row())
    return kb


def items_kb(st: dict) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup()
    items = path_node(st, 6)
    selected = st.get("item_idx")
    for i, item in enumerate(items):
        mark = "●" if selected == i else "○"
        side = "◀" if "ліва" in item["name"] else ("▶" if "права" in item["name"] else "◀▶")
        kb.add(
            types.InlineKeyboardButton(
                f"{mark} {side} {item['name']} — {price_txt(item)}",
                callback_data=f"p:item:{i}",
            )
        )
    if selected is not None:
        kb.add(
            types.InlineKeyboardButton(
                "✅ Замовити обране", callback_data="p:do_order"
            )
        )
    kb.row(*nav_row())
    return kb


def path_caption(st: dict) -> str:
    parts = [str(st[k]) for k in PATH_KEYS if k in st]
    return " → ".join(parts)


def prompt_for_step(step: str) -> str:
    return {
        "category": "Оберіть розділ:",
        "subtype": "Оберіть тип оптики:",
        "maker": "Оберіть виробника:",
        "brand": "Оберіть марку авто:",
        "model": "Оберіть модель:",
        "year": "Оберіть рік:",
        "item": "Оберіть сторону (○ / ●):",
    }[step]


def image_path_for(st: dict) -> Path:
    """Graphic banner for current step (generated PNGs, not product photos)."""
    step = st.get("step", "category")
    name = "default.png"
    if step == "category":
        name = "home.png"
    elif step == "subtype":
        name = IMG_CATEGORY.get(st.get("category", ""), "default.png")
    elif step == "maker":
        name = IMG_SUBTYPE.get(st.get("subtype", ""), "default.png")
    elif step == "brand":
        name = IMG_MAKER.get(st.get("maker", ""), "default.png")
    elif step == "model":
        name = "brand.png"
    elif step == "year":
        name = "model.png"
    elif step == "item":
        idx = st.get("item_idx")
        if idx is not None:
            item = path_node(st, 6)[idx]
            if "пара" in item["name"]:
                name = "side_pair.png"
            elif "ліва" in item["name"]:
                name = "side_l.png"
            elif "права" in item["name"]:
                name = "side_r.png"
            else:
                name = "year.png"
        else:
            name = "year.png"
    path = IMAGES / name
    if not path.exists():
        path = IMAGES / "default.png"
    return path


def send_branch(chat_id: int, st: dict, edit_msg=None) -> None:
    step = st["step"]
    cap = path_caption(st)
    head = f"<i>{cap}</i>\n\n" if cap and step != "category" else ""
    text = f"{head}{STOCK_NOTE}.\n{prompt_for_step(step)}"
    markup = items_kb(st) if step == "item" else branch_kb(st, step)
    img = image_path_for(st)

    if edit_msg is not None:
        try:
            with img.open("rb") as f:
                media = types.InputMediaPhoto(f, caption=text, parse_mode="HTML")
                bot.edit_message_media(
                    media, chat_id, edit_msg.message_id, reply_markup=markup
                )
            return
        except Exception:
            try:
                bot.delete_message(chat_id, edit_msg.message_id)
            except Exception:
                pass

    with img.open("rb") as f:
        bot.send_photo(chat_id, f, caption=text, reply_markup=markup)


def start_catalog(chat_id: int, uid: int) -> None:
    sessions[uid] = {"step": "category"}
    send_branch(chat_id, sessions[uid])


def begin_order_form(chat_id: int, uid: int) -> None:
    st = sessions[uid]
    item = path_node(st, 6)[st["item_idx"]]
    st["item"] = item
    st["step"] = "first_name"
    caption = (
        f"Обрано: <b>{item['name']}</b>\n"
        f"{path_caption(st)}\n"
        f"Ціна: {price_txt(item)}\n{STOCK_NOTE}\n\n"
        "Введіть <b>імʼя</b>:"
    )
    img = IMAGES / "order.png"
    if not img.exists():
        img = IMAGES / "default.png"
    with img.open("rb") as f:
        bot.send_photo(chat_id, f, caption=caption, reply_markup=input_kb())


@bot.message_handler(commands=["start", "help", "menu"])
def cmd_start(message: telebot.types.Message) -> None:
    reset(message.from_user.id)
    caption = (
        "<b>Демо: автолінзи / оптика</b>\n"
        f"{STOCK_NOTE}.\n\n"
        "Синя <b>Menu</b> зліва або «Каталог».\n"
        "Картинки — графіка (не фото товарів).\n"
        "Основна оптика / ПТФ → тип → виробник → авто → сторона → заявка."
    )
    img = IMAGES / "home.png"
    if img.exists():
        with img.open("rb") as f:
            bot.send_photo(
                message.chat.id, f, caption=caption, reply_markup=main_kb()
            )
    else:
        bot.send_message(message.chat.id, caption, reply_markup=main_kb())


@bot.message_handler(commands=["cancel"])
def cmd_cancel(message: telebot.types.Message) -> None:
    reset(message.from_user.id)
    bot.send_message(message.chat.id, "Скасовано.", reply_markup=main_kb())


@bot.message_handler(commands=["catalog"])
@bot.message_handler(func=lambda m: m.text == "🛍 Каталог")
def cmd_catalog(message: telebot.types.Message) -> None:
    start_catalog(message.chat.id, message.from_user.id)


@bot.message_handler(commands=["order"])
def cmd_order(message: telebot.types.Message) -> None:
    st = sessions.get(message.from_user.id) or {}
    if st.get("item_idx") is not None and "year" in st:
        begin_order_form(message.chat.id, message.from_user.id)
    else:
        bot.send_message(
            message.chat.id,
            "Спочатку оберіть товар у каталозі (●).",
            reply_markup=main_kb(),
        )
        start_catalog(message.chat.id, message.from_user.id)


@bot.message_handler(func=lambda m: m.text == "🚚 Доставка")
def delivery(message: telebot.types.Message) -> None:
    bot.send_message(
        message.chat.id,
        "<b>Доставка</b>\nНова Пошта на відділення.\n"
        "У заявці: місто та номер відділення.",
        reply_markup=main_kb(),
    )


@bot.message_handler(func=lambda m: m.text == "📞 Контакти")
def contacts(message: telebot.types.Message) -> None:
    bot.send_message(
        message.chat.id,
        "<b>Контакти</b>\nЗаявка через каталог → менеджер у Telegram.",
        reply_markup=main_kb(),
    )


@bot.message_handler(func=lambda m: m.text == BTN_HOME)
def go_home(message: telebot.types.Message) -> None:
    cmd_start(message)


@bot.message_handler(func=lambda m: m.text == BTN_CANCEL)
def go_cancel(message: telebot.types.Message) -> None:
    cmd_cancel(message)


@bot.message_handler(func=lambda m: m.text == BTN_BACK)
def text_back(message: telebot.types.Message) -> None:
    uid = message.from_user.id
    st = sessions.get(uid)
    if not st:
        cmd_start(message)
        return
    step = st.get("step")
    if step in ORDER_STEPS:
        i = ORDER_STEPS.index(step)
        if i == 0:
            st["step"] = "item"
            send_branch(message.chat.id, st)
            return
        st["step"] = ORDER_STEPS[i - 1]
        prompts = {
            "first_name": "Введіть <b>імʼя</b>:",
            "last_name": "Введіть <b>прізвище</b>:",
            "phone": "Введіть <b>телефон</b> (+380…):",
            "city": "Введіть <b>місто</b>:",
            "np": "Введіть <b>відділення Нової Пошти</b>:",
        }
        bot.send_message(
            message.chat.id, prompts[st["step"]], reply_markup=input_kb()
        )
        return
    cmd_start(message)


@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("p:"))
def on_pick(call: telebot.types.CallbackQuery) -> None:
    uid = call.from_user.id
    chat_id = call.message.chat.id
    data = call.data.split(":")
    action = data[1]

    if action == "home":
        reset(uid)
        bot.answer_callback_query(call.id)
        try:
            bot.edit_message_reply_markup(
                chat_id, call.message.message_id, reply_markup=None
            )
        except Exception:
            pass
        cmd_start(call.message)
        return

    st = sessions.get(uid)
    if not st:
        bot.answer_callback_query(call.id, "Почніть з /catalog")
        start_catalog(chat_id, uid)
        return

    if action == "back":
        step = st.get("step", "category")
        if step == "item":
            st.pop("item_idx", None)
            st.pop("item", None)
            st["step"] = "year"
        else:
            idx = STEPS.index(step)
            if idx <= 0:
                reset(uid)
                bot.answer_callback_query(call.id)
                cmd_start(call.message)
                return
            for k in list(STEPS[idx:]) + ["item_idx", "item"]:
                st.pop(k, None)
            st["step"] = STEPS[idx - 1]
        bot.answer_callback_query(call.id)
        send_branch(chat_id, st, edit_msg=call.message)
        return

    if action == "do_order":
        if st.get("item_idx") is None:
            bot.answer_callback_query(call.id, "Спочатку оберіть ●")
            return
        bot.answer_callback_query(call.id)
        begin_order_form(chat_id, uid)
        return

    if action in STEPS:
        try:
            i = int(data[2])
        except (IndexError, ValueError):
            bot.answer_callback_query(call.id, "Помилка")
            return
        labels = labels_at(st, action)
        if i < 0 or i >= len(labels):
            bot.answer_callback_query(call.id, "Немає пункту")
            return

        if action == "item":
            st["item_idx"] = i
            st["step"] = "item"
            bot.answer_callback_query(call.id, "Обрано")
            send_branch(chat_id, st, edit_msg=call.message)
            return

        st[action] = labels[i]
        st["step"] = STEPS[STEPS.index(action) + 1]
        st.pop("item_idx", None)
        bot.answer_callback_query(call.id)
        send_branch(chat_id, st, edit_msg=call.message)
        return

    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda m: True, content_types=["text"])
def wizard(message: telebot.types.Message) -> None:
    uid = message.from_user.id
    text = (message.text or "").strip()
    st = sessions.get(uid)

    if not st or st.get("step") not in ORDER_STEPS:
        bot.send_message(
            message.chat.id,
            "Оберіть пункт меню або /catalog",
            reply_markup=main_kb(),
        )
        return

    step = st["step"]

    if step == "first_name":
        st["first_name"] = text
        st["step"] = "last_name"
        bot.send_message(
            message.chat.id, "Введіть <b>прізвище</b>:", reply_markup=input_kb()
        )
        return

    if step == "last_name":
        st["last_name"] = text
        st["step"] = "phone"
        bot.send_message(
            message.chat.id,
            "Введіть <b>телефон</b> (+380…):",
            reply_markup=input_kb(),
        )
        return

    if step == "phone":
        st["phone"] = text
        st["step"] = "city"
        bot.send_message(
            message.chat.id, "Введіть <b>місто</b>:", reply_markup=input_kb()
        )
        return

    if step == "city":
        st["city"] = text
        st["step"] = "np"
        bot.send_message(
            message.chat.id,
            "Введіть <b>відділення Нової Пошти</b> (номер або адреса):",
            reply_markup=input_kb(),
        )
        return

    if step == "np":
        st["np"] = text
        item = st["item"]
        user = message.from_user
        who = f"@{user.username}" if user.username else f"id={uid}"
        admin = (
            "<b>Нова заявка — автолінзи</b>\n"
            f"{STOCK_NOTE}\n\n"
            f"Шлях: {path_caption(st)}\n"
            f"Товар: {item['name']} ({item['id']})\n"
            f"Ціна: {price_txt(item)}\n\n"
            f"Імʼя: {st['first_name']}\n"
            f"Прізвище: {st['last_name']}\n"
            f"Телефон: {st['phone']}\n"
            f"Місто: {st['city']}\n"
            f"НП: {st['np']}\n\n"
            f"Клієнт TG: {who}"
        )
        bot.send_message(ADMIN_CHAT_ID, admin)
        bot.send_message(
            message.chat.id,
            "Дякуємо! Заявку надіслано менеджеру.\n"
            "Уточнимо комплектацію і відправку Новою Поштою.",
            reply_markup=main_kb(),
        )
        reset(uid)


if __name__ == "__main__":
    print("Autolens demo bot polling…")
    bot.infinity_polling(skip_pending=True)