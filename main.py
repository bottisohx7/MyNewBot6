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
user_selection = {} # برای ذخیره وضعیت انتخاب کاربر

# --- مدیریت دیتابیس ---
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

# --- منوی اصلی (مشابه ربات مرجع) ---
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

# --- پردازش دستورات ---
@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "سلام، شاهد! 👋\n"
        "من یک ربات پیشرفته هستم که از ابزارهای هوش مصنوعی برای ویرایش عکس‌های شما استفاده می‌کنم.\n\n"
        "✅ گزینه خود را از زیر انتخاب کنید:"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id
    if call.data == "profile":
        credit = get_credit(user_id)
        bot.send_message(call.message.chat.id, f"👤 اعتبار موجود: {credit}\n🆔 شناسه: {user_id}")
    elif call.data in ["remove_bg", "enhance", "nude_gen"]:
        user_selection[user_id] = call.data
        bot.send_message(call.message.chat.id, f"✅ حالت {call.data} انتخاب شد. لطفاً عکس خود را بفرستید.")
    else:
        bot.answer_callback_query(call.id, "این قابلیت به‌زودی فعال می‌شود!")

# --- پردازش تصاویر ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    action = user_selection.get(user_id)

    if not action:
        bot.reply_to(message, "⚠️ لطفاً ابتدا از منوی اصلی یک گزینه را انتخاب کنید.")
        return

    if get_credit(user_id) <= 0:
        bot.reply_to(message, "❌ اعتبار شما تمام شده است. لطفاً دعوت کنید یا اعتبار بخرید.")
        return

    msg = bot.reply_to(message, "⏳ در حال پردازش توسط هوش مصنوعی...")
    
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        
        # انتخاب مدل بر اساس انتخاب کاربر
        if action == "remove_bg":
            output = replicate.run("cjwbw/rembg:fb8af69c9b13970b8a3e74640d2105193910c27943d2c88219016e78864d4206", input={"image": photo_url})
        else: # پیش فرض بهبود کیفیت
            output = replicate.run("tencentarc/gfpgan:928360806b745499256956627685655938d227c88b776269661d9a5996d9943f", input={"img": photo_url})
        
        reduce_credit(user_id)
        bot.send_message(message.chat.id, f"✅ نتیجه آماده شد:\n{output}")
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.reply_to(message, f"❌ خطا در پردازش: {e}")
    finally:
        user_selection[user_id] = None

bot.infinity_polling()
