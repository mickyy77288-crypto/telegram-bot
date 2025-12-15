# -*- coding: utf-8 -*-
# =====================================================
# Telegram Username Generator Bot
# ВЕРСИЯ ДЛЯ PYTHON 3.12 / 3.13
# python-telegram-bot >= 21.x
# =====================================================
# УСТАНОВКА:
# pip install -U python-telegram-bot
#
# 1. Вставь TOKEN
# 2. Запусти файл
# =====================================================

import random
import string
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.error import BadRequest

# ================== НАСТРОЙКИ ==================
TOKEN = "8402345893:AAHengfyXzgaHMBQS6JzwXqpLP-tNgkaLR4"
MIN_RESULTS = 100

user_states: dict[int, dict] = {}

# ================== ФУНКЦИИ ==================

def generate_username(word: str, length: int) -> str:
    chars = string.ascii_lowercase + string.digits
    extra_len = max(0, length - len(word))
    extra = ''.join(random.choice(chars) for _ in range(extra_len))
    return (word + extra)[:length]


async def is_username_free(bot, username: str) -> bool:
    try:
        await bot.get_chat(f"@{username}")
        return False
    except BadRequest:
        return True
    except Exception:
        return False

# ================== ХЕНДЛЕРЫ ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Поиск юзернеймов", callback_data="search")],
        [InlineKeyboardButton("📜 Список команд", callback_data="commands")],
    ]

    await update.message.reply_text(
        "👋 Привет!\n"
        "Я найду минимум 100 свободных Telegram-юзернеймов 🚀",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "search":
        user_states[query.from_user.id] = {"step": "word"}
        await query.message.reply_text("✏️ Введи слово для юзернейма:")

    elif query.data == "commands":
        await query.message.reply_text(
            "/start — главное меню\n"
            "Поиск юзернеймов — генерация свободных ников"
        )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text.lower().replace("@", "")

    if uid not in user_states:
        return

    state = user_states[uid]

    # ШАГ 1 — СЛОВО
    if state["step"] == "word":
        state["word"] = text
        state["step"] = "length"
        await update.message.reply_text("🔢 Сколько символов должен содержать юзернейм?")
        return

    # ШАГ 2 — ДЛИНА
    if state["step"] == "length":
        if not text.isdigit():
            await update.message.reply_text("❌ Введи число")
            return

        length = int(text)
        word = state["word"]

        if length < len(word) or length < 5 or length > 32:
            await update.message.reply_text("❌ Длина должна быть от 5 до 32 и не меньше слова")
            return

        await update.message.reply_text("⏳ Генерирую минимум 100 свободных юзернеймов...")

        found: list[str] = []
        attempts = 0
        max_attempts = MIN_RESULTS * 20

        while len(found) < MIN_RESULTS and attempts < max_attempts:
            username = generate_username(word, length)
            if username not in found:
                if await is_username_free(context.bot, username):
                    found.append(username)
            attempts += 1

        if found:
            result = "\n".join(f"@{u}" for u in found)
            await update.message.reply_text(
                f"✅ Найдено {len(found)}+ свободных юзернеймов:\n\n{result}"
            )
        else:
            await update.message.reply_text("❌ Не удалось найти свободные юзернеймы")

        user_states.pop(uid, None)

# ================== ЗАПУСК ==================

# ВАЖНО: для Python 3.13 + Windows НЕ используем asyncio.run
# python-telegram-bot сам управляет event loop

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Бот запущен (Python 3.13, stable)")
    app.run_polling()


if __name__ == "__main__":
    main()
