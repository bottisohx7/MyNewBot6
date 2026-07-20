Import sqlite3
import telebot
from telebot import types
import replicate
import os

# --- تنظیمات ---
BOT_TOKEN = "8911090985:AAHgWUcH-hZmg_iINZZ5SWOmu6fBZUaSesI"
REPLICATE_API_TOKEN = "r8_PwLrrwfl8Zy1LrtVvyEJI2lK2xnOGzi2FwfSV"
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)

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

# --- منو ---
def main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("تعویض چهره 🎭", callback_data="swap_face"),
               types.InlineKeyboardButton("حذف پس‌زمینه 🖼️", callback_data="remove_bg"))
    markup.row(types.InlineKeyboardButton("بهبود کیفیت عکس ✨", callback_data="enhance"))
    markup.row(types.InlineKeyboardButton("حساب کاربری من 👤", callback_data="profile"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "سلام شاهد! به ربات خوش آمدید.", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "profile":
        credit = get_credit(call.from_user.id)
        bot.send_message(call.message.chat.id, f"👤 حساب کاربری شما\n💳 اعتبار: {credit}")
    elif call.data == "enhance":
        bot.send_message(call.message.chat.id, "لطفاً عکس خود را برای بهبود کیفیت بفرستید.")
    bot.answer_callback_query(call.id)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    if get_credit(user_id) <= 0:
        bot.reply_to(message, "❌ اعتبار شما تمام شده است!")
        return

    bot.reply_to(message, "⏳ در حال پردازش...")
    
    file_info = bot.get_file(message.photo[-1].file_id)
    photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

    try:
        output = replicate.run(
            "tencentarc/gfpgan:928360806b745499256956627685655938d227c88b776269661d9a5996d9943f",
            input={"img": photo_url}
        )
        reduce_credit(user_id)
        bot.reply_to(message, f"✅ نتیجه آماده شد: {output}")
    except Exception as e:
        bot.reply_to(message, f"❌ خطا: {e}")

bot.infinity_polling()
