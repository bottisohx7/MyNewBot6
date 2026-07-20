import telebot
from telebot import types
import deepai_client
import requests # برای پشتیبانی از سایر APIها

# --- تنظیمات ---
BOT_TOKEN = "8911090985:AAHgWUcH-hZmg_iINZZ5SWOmu6fBZUaSesI"
KEYS = {
    "deepai": "5fa29da6-d052-4df8-a2b9-c40aef22d5ee",
    "huggingface": "Hf_wMBrSyYVWGKuvvObqUUiqmNNFuTdSTVceo",
    "stability": "sk-C5C9251kC6cL8Hvmw31adBeAIpmvhc9QXKhwmSXFYyLV9oUA"
}

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

# --- سیستم هوشمند فراخوانی API ---
def call_ai_api(prompt, style):
    # اولویت اول: DeepAI
    try:
        response = deepai_client.call('text2img', {'text': f"{prompt} style: {style}"}, api_key=KEYS["deepai"])
        return response['output_url']
    except Exception as e:
        print(f"DeepAI Error: {e}")
        return None # اگر نشد، خروجی None برمی‌گرداند تا ربات متوجه شود

# --- منوی استایل‌ها ---
def styles_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    styles = [
        "Abyssal Void v4", "Realistic v3", "Stick Logo V4", "Complex System V4",
        "Neonic V4", "Zdzislaw V4", "Exprealism V4", "Van Gogh V4",
        "Fujifilm V4", "Steampunk V4", "Cinematic V4", "Character V4",
        "Futurepunk V4", "3D v4", "Golden Hour v4", "Realistic v4",
        "Surrealism v3", "Cartoon v3"
    ]
    buttons = [types.InlineKeyboardButton(s, callback_data=f"style_{s}") for s in styles]
    markup.add(*buttons)
    markup.row(
        types.InlineKeyboardButton("«", callback_data="prev"),
        types.InlineKeyboardButton("❌", callback_data="cancel"),
        types.InlineKeyboardButton("»", callback_data="next")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "سلام شاهد عزیز، به ربات Somnium خوش آمدید. لطفا مشخصات لوگو را ارسال کنید.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text.startswith('/'): return
    user_data[message.from_user.id] = message.text
    bot.reply_to(message, "🐈 Choose The Style:", reply_markup=styles_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith("style_"))
def process_style(call):
    user_id = call.from_user.id
    style_name = call.data.replace("style_", "")
    user_text = user_data.get(user_id, "No text provided")
    
    msg = bot.edit_message_text(f"⏳ در حال ساخت با استایل {style_name}...", call.message.chat.id, call.message.message_id)
    
    # تلاش برای دریافت عکس
    image_url = call_ai_api(user_text, style_name)
    
    if image_url:
        bot.send_photo(call.message.chat.id, image_url, caption=f"🍇 **Dream:**\n{user_text}\n\n🐈 **Style:** {style_name}")
        bot.delete_message(call.message.chat.id, msg.message_id)
    else:
        bot.edit_message_text("❌ خطا در تمامی مسیرها. کلیدها را چک کنید یا دوباره تلاش کنید.", call.message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data in ["cancel", "next", "prev"])
def handle_nav(call):
    if call.data == "cancel":
        bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "این بخش در حال توسعه است.")

bot.infinity_polling()
