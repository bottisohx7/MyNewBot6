import sqlite3
import telebot
from telebot import types
import replicate
import os

# --- تنظیمات ---
BOT_TOKEN = "8911090985:AAHgWUcH-hZmg_iINZZ5SWOmu6fBZUaSesI"
REPLICATE_API_TOKEN = "r8_PwLrrwfl8Zy1LrtVvyEJI2lK2xnOGzi2FwfSV"
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)
user_selection = {} # ذخیره انتخاب کاربر

# --- دیتابیس ---
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

def reduce_credit(user_id):
    cursor.execute("UPDATE users SET credit = credit - 1 WHERE id=?", (user_id,))
    conn.commit()

# --- منوی اصلی ---
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

# --- هندلرها ---
@bot.message_handler(commands=['start'])
def start(message):
    text = "سلام، شاهد! 👋\n✅ گزینه خود را از زیر انتخاب کنید:"
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "profile":
        credit = get_credit(call.from_user.id)
        bot.send_message(call.message.chat.id, f"👤 اعتبار موجود: {credit}")
    elif call.data in ["remove_bg", "enhance"]:
        user_selection[call.from_user.id] = call.data
        bot.send_message(call.message.chat.id, f"لطفاً عکس خود را برای {call.data} بفرستید.")
    else:
        bot.answer_callback_query(call.id, "این قابلیت به‌زودی فعال می‌شود!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    action = user_selection.get(user_id)

    if not action:
        bot.reply_to(message, "ابتدا از منو یک گزینه انتخاب کنید.")
        return

    if get_credit(user_id) <= 0:
        bot.reply_to(message, "❌ اعتبار شما تمام شده است!")
        return

    bot.reply_to(message, "⏳ در حال پردازش توسط هوش مصنوعی...")
    
    file_info = bot.get_file(message.photo[-1].file_id)
    photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

    try:
        if action == "remove_bg":
            output = replicate.run("lucataco/rembg:95fcc2a26d3899cd6c2691c900465aa0433ae190226b5d920366838d423985a9", input={"image": photo_url})
        else: # enhance
            output = replicate.run("tencentarc/gfpgan:928360806b745499256956627685655938d227c88b776269661d9a5996d9943f", input={"img": photo_url})
        
        reduce_credit(user_id)
        bot.reply_to(message, f"✅ نتیجه:\n{output}")
        user_selection[user_id] = None
    except Exception as e:
        bot.reply_to(message, f"❌ خطا: {e}")

bot.infinity_polling()
