import os
import sqlite3
import telebot
from telebot import types
import replicate

# --- تنظیمات ---
BOT_TOKEN = "8911090985:AAHgWUcH-hZmg_iINZZ5SWOmu6fBZUaSesI"
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN") or "r8_PwLrrwfl8Zy1LrtVvyEJI2lK2xnOGzi2FwfSV"

bot = telebot.TeleBot(BOT_TOKEN)
user_selection = {}

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
    text = (
        "سلام، شاهد! 👋\n"
        "من یک ربات پیشرفته تلگرام هستم که از ابزارهای هوش مصنوعی برای کمک به شما در تبدیل فوری و رایگان عکس‌هایتان استفاده می‌کنم.\n\n"
        "ویژگی‌ها ✨\n"
        "🔸 بهبود کیفیت عکس HD\n"
        "🔸 حذف واترمارک و متن\n"
        "🔸 حذف پس‌زمینه\n"
        "🔸 تغییر لباس و پوشاک\n"
        "🔸 عکس به بر*هنه (بر*هنه ساز)\n"
        "🔸 تعویض دو چهره\n\n"
        "✅ گزینه خود را از زیر انتخاب کنید:"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id
    if call.data == "profile":
        credit = get_credit(user_id)
        text = (
            f"👤 حساب کاربری من\n\n"
            f"💳 اعتبار موجود: {credit}\n"
            f"👥 کل دعوت‌ها: 0\n"
            f"🆔 شناسه چت: {user_id}\n"
            f"🔗 لینک دعوت: https://t.me/Edit_With_Ai_Bot?start={user_id}\n\n"
            f"📌 1 دعوت = 1 اعتبار\n"
            f"⚡ برای دریافت اعتبار بیشتر، کاربران را با لینک دعوت خود دعوت کنید\n\n"
            f"💎 شما همچنین می‌توانید اعتبار را با قیمت ارزان از @Kaliboy002 بخرید"
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=main_menu())
    
    elif call.data in ["nude_gen", "swap_face", "remove_wm", "remove_bg", "change_cloth", "enhance"]:
        user_selection[user_id] = call.data
        bot.answer_callback_query(call.id, f"✅ گزینه {call.data} انتخاب شد. حالا عکس خود را بفرستید.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    action = user_selection.get(user_id)
    if not action:
        bot.reply_to(message, "⚠️ ابتدا از منو یک گزینه انتخاب کنید.")
        return
    
    msg = bot.reply_to(message, "⏳ در حال پردازش تصویر توسط هوش مصنوعی...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        client = replicate.Client(api_token=REPLICATE_API_TOKEN)
        
        # مدل‌های فعال برای هر گزینه
        if action == "remove_bg":
            output = client.run("cjwbw/rembg:fb8af69c9b13970b8a3e74640d2105193910c27943d2c88219016e78864d4206", input={"image": photo_url})
        elif action == "enhance":
            output = client.run("tencentarc/gfpgan:928360806b745499256956627685655938d227c88b776269661d9a5996d9943f", input={"img": photo_url})
        else:
            bot.send_message(message.chat.id, "این قابلیت در حال حاضر در حال توسعه است.")
            bot.delete_message(message.chat.id, msg.message_id)
            return

        bot.send_message(message.chat.id, f"✅ نتیجه آماده شد:\n{output}")
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.reply_to(message, f"❌ خطا در ارتباط با هوش مصنوعی: {e}")
    finally:
        user_selection[user_id] = None

bot.infinity_polling()
