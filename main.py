import sqlite3
import telebot
from telebot import types
import replicate
import os

BOT_TOKEN = "8911090985:AAHgWUcH-hZmg_iINZZ5SWOmu6fBZUaSesI"
REPLICATE_API_TOKEN = "r8_PwLrrwfl8Zy1LrtVvyEJI2lK2xnOGzi2FwfSV"
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)

# --- دیتابیس (مشابه قبل) ---
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, credit INTEGER)")
conn.commit()

def get_credit(user_id):
    cursor.execute("SELECT credit FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    if row: return row[0]
    cursor.execute("INSERT INTO users VALUES (?, ?)", (user_id, 3))
    conn.commit()
    return 3

# --- منوی کامل (مثل ربات مرجع) ---
def main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("بر*هنه ساز 👙", callback_data="nude_gen"),
               types.InlineKeyboardButton("تعویض چهره 🎭", callback_data="swap_face"))
    markup.row(types.InlineKeyboardButton("حذف واترمارک 💧", callback_data="remove_wm"),
               types.InlineKeyboardButton("حذف پس‌زمینه 🖼️", callback_data="remove_bg"))
    markup.row(types.InlineKeyboardButton("تغییر لباس 👗", callback_data="change_cloth"),
               types.InlineKeyboardButton("بهبود عکس ✨", callback_data="enhance"))
    markup.row(types.InlineKeyboardButton("حساب کاربری من 👤", callback_data="profile"),
               types.InlineKeyboardButton("زبان 🌐", callback_data="lang"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "سلام، شاهد! 👋\n\n"
        "🚀 من یک ربات پیشرفته هستم که از ابزارهای هوش مصنوعی برای ویرایش عکس‌های شما استفاده می‌کنم.\n\n"
        "✅ گزینه خود را از زیر انتخاب کنید:"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "profile":
        credit = get_credit(call.from_user.id)
        text = (f"👤 حساب کاربری شما\n"
                f"💳 اعتبار موجود: {credit}\n"
                f"🆔 شناسه چت: {call.from_user.id}\n\n"
                f"⚡ برای دریافت اعتبار بیشتر، لینک دعوت خود را پخش کنید.")
        bot.send_message(call.message.chat.id, text)
    else:
        bot.answer_callback_query(call.id, "این قابلیت به‌زودی فعال می‌شود!")

bot.infinity_polling()
