import os
import sqlite3
import telebot
from telebot import types
import replicate

# --- تنظیمات ---
BOT_TOKEN = "8911090985:AAHgWUcH-hZmg_iINZZ5SWOmu6fBZUaSesI"
API_TOKEN = "r8_ec3ZsZ8kWfQRAzptdUyqKYlaFVT7zMP4QlNMp"

bot = telebot.TeleBot(BOT_TOKEN)

# ذخیره موقت متن کاربر برای پردازش در مرحله بعد
user_prompts = {}

# --- منوی دکمه‌های استایل (دقیقاً مطابق عکس‌های Somnium) ---
def styles_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        types.InlineKeyboardButton("Abyssal Void v4", callback_data="style_Abyssal Void v4"),
        types.InlineKeyboardButton("Realistic v3", callback_data="style_Realistic v3"),
        types.InlineKeyboardButton("Stick Logo V4", callback_data="style_Stick Logo V4"),
        types.InlineKeyboardButton("Complex System V4", callback_data="style_Complex System V4"),
        types.InlineKeyboardButton("Neonic V4", callback_data="style_Neonic V4"),
        types.InlineKeyboardButton("Zdzislaw V4", callback_data="style_Zdzislaw V4"),
        types.InlineKeyboardButton("Exprealism V4", callback_data="style_Exprealism V4"),
        types.InlineKeyboardButton("Van Gogh V4", callback_data="style_Van Gogh V4"),
        types.InlineKeyboardButton("Fujifilm V4", callback_data="style_Fujifilm V4"),
        types.InlineKeyboardButton("Steampunk V4", callback_data="style_Steampunk V4"),
        types.InlineKeyboardButton("Cinematic V4", callback_data="style_Cinematic V4"),
        types.InlineKeyboardButton("Character V4", callback_data="style_Character V4"),
        types.InlineKeyboardButton("Futurepunk V4", callback_data="style_Futurepunk V4"),
        types.InlineKeyboardButton("3D v4", callback_data="style_3D v4"),
        types.InlineKeyboardButton("Golden Hour v4", callback_data="style_Golden Hour v4"),
        types.InlineKeyboardButton("Realistic v4", callback_data="style_Realistic v4"),
        types.InlineKeyboardButton("Surrealism v3", callback_data="style_Surrealism v3"),
        types.InlineKeyboardButton("Cartoon v3", callback_data="style_Cartoon v3")
    )
    
    # دکمه‌های ناوبری پایین منو (صفحه قبل، حذف، صفحه بعد)
    markup.row(
        types.InlineKeyboardButton("«", callback_data="prev_page"),
        types.InlineKeyboardButton("❌", callback_data="cancel"),
        types.InlineKeyboardButton("»", callback_data="next_page")
    )
    return markup

# --- پیام شروع ---
@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "سلام شاهد عزیز به ربات طراحی لوگو و عکس Somnium خوش آمدید! 👋\n\n"
        "لطفاً متن مورد نظر خود را ارسال کنید (مانند نمونه زیر):\n\n"
        "Main Name (Center): REIS SHAHID\n"
        "Secondary Text (Lower Banner): SHADOW CORE\n"
        "Upper Monogram: RS"
    )
    bot.send_message(message.chat.id, text)

# --- دریافت متن کاربر ---
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    user_prompts[user_id] = message.text  # ذخیره متن فرستاده شده
    
    # نمایش منوی انتخاب استایل مشابه عکس شما
    bot.reply_to(message, "🐈 Choose The Style:", reply_markup=styles_menu())

# --- مدیریت انتخاب استایل و ساخت عکس ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("style_"))
def process_style(call):
    user_id = call.from_user.id
    style_name = call.data.replace("style_", "")
    
    # بررسی اینکه آیا کاربر از قبل متنی فرستاده است یا خیر
    user_text = user_prompts.get(user_id)
    if not user_text:
        bot.answer_callback_query(call.id, "⚠️ ابتدا متن خود را ارسال کنید.")
        return

    # آپدیت پیام به وضعیت در حال پردازش
    bot.edit_message_text(
        chat_id=call.message.chat.id, 
        message_id=call.message.message_id, 
        text=f"⚡ Style: {style_name}\n\n⏳ در حال ساخت تصویر شما، لطفاً شکیبا باشید..."
    )
    
    try:
        # اتصال به کلاینت Replicate
        client = replicate.Client(api_token=API_TOKEN)
        
        # ترکیب متن کاربر با استایل انتخاب شده برای ساخت پرامپت دقیق هوش مصنوعی
        full_prompt = f"Logo design, text typography layout. Text details: {user_text}. Style: {style_name}, highly detailed, 4k resolution, graphic design."
        
        # استفاده از مدل قدرتمند Flux یا Stable Diffusion برای تولید متن و لوگو دقیق
        output = client.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": full_prompt,
                "aspect_ratio": "1:1",
                "output_format": "jpg"
            }
        )
        
        # ارسال عکس نهایی به همراه متن‌های مشخص شده و دکمه سورس کد
        if output and len(output) > 0:
            image_url = output[0]
            
            caption_text = (
                f"🍇 **Dream:**\n{user_text}\n\n"
                f"🐈 **Style:** {style_name}"
            )
            
            # دکمه شیشه‌ای زیر عکس نهایی
            final_markup = types.InlineKeyboardMarkup()
            final_markup.add(types.InlineKeyboardButton("Source Code ↗️", url="https://github.com"))
            
            bot.send_photo(call.message.chat.id, image_url, caption=caption_text, parse_mode="Markdown", reply_markup=final_markup)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            
        else:
            bot.send_message(call.message.chat.id, "❌ مشکلی در تولید تصویر به وجود آمد.")
            
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ خطا در اتصال به هوش مصنوعی:\n{str(e)[:100]}")
    
    finally:
        # پاک کردن متن موقت کاربر پس از اتمام فرآیند
        if user_id in user_prompts:
            del user_prompts[user_id]

# --- مدیریت دکمه خروج/لغو ---
@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def cancel_action(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="❌ عملیات لغو شد. می‌توانید متن جدیدی بفرستید.")

bot.infinity_polling()
