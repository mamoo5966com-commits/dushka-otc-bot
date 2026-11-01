import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from flask import Flask
from threading import Thread

# بيانات البوت والقناة التجريبية
TOKEN = "9086361088:AAErE0hgvSzCkCCSlobAxxK5gZXg6h6bvnM"
CHANNEL_ID = "@doshkotc"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is active and running 24/7!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- لوحة التحكم الخاصة بك كمشرف ---
def main_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("🚀 فحص الـ OTC وإرسال إشارة", callback_data="send_signal"),
        InlineKeyboardButton("📊 إحصائيات الجلسة", callback_data="stats")
    )
    markup.add(
        InlineKeyboardButton("⚠️ تنبيه للمشتركين (بدء الجلسة)", callback_data="session_start")
    )
    return markup

# --- أمر التشغيل /start ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_msg = (
        f"🙋‍♂️ أهلاً بك يا كابتن في لوحة تحكم **Dushka OTC Bot**\n\n"
        f"البوت يعمل الآن **سحابياً 24/7** ومتصل بقناتك: `{CHANNEL_ID}`\n"
        f"اختر من القائمة أدناه لتجربة الإرسال:"
    )
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=main_keyboard())

# --- معالجة الأزرار التفاعلية ---
@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    if call.data == "send_signal":
        bot.answer_callback_query(call.id, "جاري فحص المستويات وإرسال التوصية...")
        
        signal_template = (
            "🎯 **توصية OTC جديدة - Dushka VIP** 🎯\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💱 **الزوج:** EUR/USD-OTC\n"
            "🟢 **الاتجاه:** شراء / صعود (CALL)\n"
            "⏰ **مدة الصفقة:** 5 دقائق (فريم M5)\n"
            "📍 **السبب الفني:** ارتداد من دعم قوي + إعادة اختبار كسر المقاومة (Breakout & Retest)\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ *تنبيه: التزم بإدارة رأس المال (1-3% من المحفظة فقط).* \n"
            "🔗 رابط المنصة: [Quotex](https://quotex.com)"
        )
        
        try:
            bot.send_message(CHANNEL_ID, signal_template, parse_mode="Markdown", disable_web_page_preview=True)
            bot.send_message(message_chat_id := call.message.chat.id, "✅ تم إرسال التوصية بنجاح إلى القناة التجريبية!")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ حدث خطأ أثناء الإرسال! تأكد أن البوت مشرف في القناة.\nالخطأ: {e}")

    elif call.data == "session_start":
        bot.answer_callback_query(call.id, "إرسال تنبيه بدء الجلسة...")
        start_notice = (
            "🚨 **تنبيه لجميع الأعضاء** 🚨\n\n"
            "ستبدأ جلسة صفقات الـ OTC خلال 10 دقائق من الآن.\n"
            "يرجى تجهيز حساب المنصة والالتزام التام بالتعليمات وإدارة رأس المال! 🔥"
        )
        bot.send_message(CHANNEL_ID, start_notice, parse_mode="Markdown")
        bot.send_message(call.message.chat.id, "📢 تم نشر تنبيه بدء الجلسة بالقناة!")

    elif call.data == "stats":
        bot.answer_callback_query(call.id, "عرض الإحصائيات")
        bot.send_message(call.message.chat.id, "📈 **نتائج جلسة الـ OTC الأخيرة:**\n- إجمالي الصفقات: 5\n- الصفقات الناجحة: 4 ✅\n- الصفقات الخاسرة: 1 ❌\n- نسبة النجاح: 80%")

if __name__ == '__main__':
    # تحديث ملف المتطلبات ليتضمن Flask
    t = Thread(target=run_web)
    t.start()
    print("🤖 Cloud OTC Bot with Web Server is active...")
    bot.infinity_polling()
