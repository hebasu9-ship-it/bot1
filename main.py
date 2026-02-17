import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import qrcode
from io import BytesIO
import os
import logging
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# التوكن من متغيرات البيئة
TOKEN = os.environ.get('TELEGRAM_TOKEN', '8564942025:AAGjfEwnOIUw7P0jD9ihHVHiEiXKIs-zJsg')
bot = telebot.TeleBot(TOKEN)

# ===== دالة إنشاء الباركود =====
def create_qr_code(text):
    """تحويل النص إلى باركود وإرجاع الصورة كـ BytesIO"""
    try:
        # إنشاء الباركود
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        # إنشاء الصورة
        img = qr.make_image(fill_color="black", back_color="white")
        
        # حفظ الصورة في الذاكرة (بدون حفظها على القرص)
        bio = BytesIO()
        bio.name = 'qrcode.png'
        img.save(bio, 'PNG')
        bio.seek(0)
        
        return bio
    except Exception as e:
        logger.error(f"خطأ في إنشاء الباركود: {e}")
        return None

# ===== أزرار البوت =====
def main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("🔗 إنشاء باركود")
    btn2 = KeyboardButton("🕒 الوقت")
    btn3 = KeyboardButton("ℹ️ معلومات")
    btn4 = KeyboardButton("❓ مساعدة")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# ===== معالج أمر /start =====
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
🎯 *مرحباً بك في بوت تحويل الروابط إلى باركود!*

📱 *مميزات البوت:*
• تحويل أي رابط إلى باركود QR
• سهولة الاستخدام
• مجاني تماماً

🔹 *للاستخدام:*
أرسل لي أي رابط وسأحوله لك إلى باركود
أو استخدم الأزرار أدناه
    """
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=main_keyboard(),
        parse_mode='Markdown'
    )

# ===== معالج أمر /help =====
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
❓ *مساعدة البوت:*

🔹 *الأوامر المتاحة:*
• /start - بدء المحادثة
• /help - عرض هذه المساعدة
• /qr [الرابط] - إنشاء باركود لرابط

🔹 *طريقة الاستخدام:*
1. أرسل لي أي رابط (مثل: https://google.com)
2. أو استخدم الأمر: /qr https://example.com
3. سأقوم بإنشاء الباركود وإرساله لك فوراً

✅ *الروابط المدعومة:*
• روابط المواقع (https://...)
• روابط التليغرام
• أي نص طويل (سيتم تحويله أيضاً)
    """
    bot.send_message(
        message.chat.id,
        help_text,
        parse_mode='Markdown'
    )

# ===== معالج أمر /qr =====
@bot.message_handler(commands=['qr'])
def handle_qr_command(message):
    # استخراج الرابط من الأمر
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(
            message,
            "⚠️ *الاستخدام الصحيح:*\n`/qr https://example.com`\nأو أرسل الرابط مباشرة",
            parse_mode='Markdown'
        )
        return
    
    url = parts[1].strip()
    process_url(message, url)

# ===== دالة معالجة الرابط =====
def process_url(message, url):
    """معالجة الرابط وإنشاء الباركود"""
    
    # إرسال رسالة "جاري المعالجة"
    processing_msg = bot.reply_to(message, "⏳ *جاري إنشاء الباركود...*", parse_mode='Markdown')
    
    # إنشاء الباركود
    qr_image = create_qr_code(url)
    
    if qr_image:
        # حذف رسالة المعالجة
        bot.delete_message(message.chat.id, processing_msg.message_id)
        
        # إرسال الباركود
        caption = f"✅ *تم إنشاء الباركود بنجاح!*\n🔗 *الرابط:* `{url}`"
        bot.send_photo(
            message.chat.id,
            qr_image,
            caption=caption,
            parse_mode='Markdown'
        )
    else:
        # في حالة حدوث خطأ
        bot.edit_message_text(
            "❌ *عذراً، حدث خطأ في إنشاء الباركود. تأكد من الرابط وحاول مرة أخرى.*",
            message.chat.id,
            processing_msg.message_id,
            parse_mode='Markdown'
        )

# ===== معالج النصوص (الروابط) =====
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text
    
    # التعامل مع أزرار الرد السريع
    if text == "🔗 إنشاء باركود":
        bot.send_message(
            message.chat.id,
            "📎 *أرسل لي الرابط الآن:*\nمثال: `https://google.com`",
            parse_mode='Markdown'
        )
    
    elif text == "🕒 الوقت":
        now = datetime.now().strftime("%H:%M:%S")
        bot.reply_to(message, f"🕒 *الوقت الآن:* {now}", parse_mode='Markdown')
    
    elif text == "ℹ️ معلومات":
        info_text = """
🤖 *معلومات البوت:*
• الإصدار: 2.0
• اللغة: Python + pyTelegramBotAPI
• الوظيفة: تحويل الروابط إلى باركود
• المطور: @your_username
        """
        bot.reply_to(message, info_text, parse_mode='Markdown')
    
    elif text == "❓ مساعدة":
        send_help(message)
    
    else:
        # التحقق إذا كان النص يبدو كرابط
        if text.startswith(('http://', 'https://', 'www.')):
            process_url(message, text)
        else:
            # إذا لم يكن رابطاً، نسأل المستخدم إذا كان يريد تحويله كـ نص
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(
                telebot.types.InlineKeyboardButton("✅ نعم", callback_data=f"convert_text:{text}"),
                telebot.types.InlineKeyboardButton("❌ لا", callback_data="cancel")
            )
            bot.send_message(
                message.chat.id,
                f"⚠️ *هل تريد تحويل النص التالي إلى باركود؟*\n`{text[:50]}...`",
                reply_markup=markup,
                parse_mode='Markdown'
            )

# ===== معالج الأزرار المضمنة =====
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("convert_text:"):
        text = call.data.split(":", 1)[1]
        bot.delete_message(call.message.chat.id, call.message.message_id)
        process_url(call.message, text)
    
    elif call.data == "cancel":
        bot.edit_message_text(
            "✅ *تم الإلغاء*",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )

# ===== للتشغيل المحلي =====
if __name__ == "__main__":
    print("✅ بوت تحويل الروابط إلى باركود يعمل...")
    bot.infinity_polling()
