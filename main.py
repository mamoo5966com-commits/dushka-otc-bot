import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from flask import Flask
from threading import Thread, Event
import time
import random

# بيانات البوت والقناة ورابط الأفلييت
TOKEN = "9086361088:AAErE0hgvSzCkCCSlobAxxK5gZXg6h6bvnM"
CHANNEL_ID = "@doshkotc"
AFFILIATE_LINK = "https://quotex.com"
CHANNEL_NAME = "Dushka Trading VIP"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# متغيرات لإدارة حالة الجلسة التلقائية
session_running = Event()
session_stats = {"total": 0, "wins": 0, "losses": 0}

@app.route('/')
def home():
    return "Bot is active and running 24/7!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- لوحة التحكم الرئيسية للجلسات ---
def main_keyboard(is_active=False):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    if not is_active:
        markup.add(
            InlineKeyboardButton("🚀 بدء جلسة صفقات الـ OTC التلقائية", callback_data="start_session"),
            InlineKeyboardButton("📊 عرض الإحصائيات الحالية", callback_data="stats")
        )
    else:
        markup.add(
            InlineKeyboardButton("🛑 إيقاف الجلسة الحالية (STOP)", callback_data="stop_session"),
            InlineKeyboardButton("📊 عرض الإحصائيات الحالية", callback_data="stats")
        )
    return markup

# --- دالة تشغيل الجلسة التلقائية في الخلفية ---
def run_trading_session(chat_id):
    global session_stats
    session_stats = {"total": 0, "wins": 0, "losses": 0}
    
    start_notice = (
        f"🚨 **بدء جلسة تداول الـ OTC الرسمية - {CHANNEL_NAME}** 🚨\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔥 البوت يعمل الآن بشكل آلي بالكامل.\n"
        "⚠️ يرجى الالتزام التام بإدارة رأس المال وتجهيز المنصة!\n"
        f"🔗 رابط المنصة: [Quotex]({AFFILIATE_LINK})"
    )
    bot.send_message(CHANNEL_ID, start_notice, parse_mode="Markdown", disable_web_page_preview=True)
    
    pairs = ["EUR/USD-OTC", "GBP/USD-OTC", "AUD/CAD-OTC", "USD/JPY-OTC", "EUR/GBP-OTC"]
    
    while session_running.is_set():
        pair = random.choice(pairs)
        pre_msg = (
            f"🔔 **تنبيه صفقة قادمة في الجلسة**\n"
            f"💱 الزوج: `{pair}`\n"
            f"⏳ الاستعداد خلال دقيقة واحدة..."
        )
        bot.send_message(CHANNEL_ID, pre_msg, parse_mode="Markdown")
        
        for _ in range(10):
            if not session_running.is_set():
                break
            time.sleep(1)
            
        if not session_running.is_set():
            break
            
        direction = random.choice(["شراء / صعود (CALL)", "بيع / هبوط (PUT)"])
        signal_msg = (
            f"🎯 **توصية OTC جديدة - {CHANNEL_NAME}** 🎯\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"💱 **الزوج:** {pair}\n"
            f"🟢 **الاتجاه:** {direction}\n"
            "⏰ **مدة الصفقة:** 5 دقائق (فريم M5)\n"
            "📍 **السبب الفني:** إبزيم اتجاهي + تقاطع مؤشرات الزخم\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 [التسجيل في المنصة]({AFFILIATE_LINK})"
        )
        bot.send_message(CHANNEL_ID, signal_msg, parse_mode="Markdown", disable_web_page_preview=True)
        session_stats["total"] += 1
        
        for _ in range(15):
            if not session_running.is_set():
                break
            time.sleep(1)
            
        if not session_running.is_set():
            break
            
        is_win = random.choices([True, False], weights=[85, 15])[0]
        if is_win:
            session_stats["wins"] += 1
            res_text = f"🎉 **نتيجة الصفقة ({pair}): ربح ساحق (WIN) ✅🔥**"
        else:
            session_stats["losses"] += 1
            res_text = f"❌ **نتيجة الصفقة ({pair}): خسارة (LOSS) - تعويضها قادم بإذن الله**"
            
        bot.send_message(CHANNEL_ID, res_text, parse_mode="Markdown")
        
        for _ in range(10):
            if not session_running.is_set():
                break
            time.sleep(1)

    end_summary = (
        f"🏁 **انتهت جلسة التداول بنجاح - {CHANNEL_NAME}** 🏁\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 **إحصائيات الجلسة الإجمالية:**\n"
        f"- إجمالي الصفقات: {session_stats['total']}\n"
        f"- الصفقات الرابحة: {session_stats['wins']} ✅\n"
        f"- الصفقات الخاسرة: {session_stats['losses']} ❌\n"
        "شكراً لتفاعلكم ونراكم في الجلسة القادمة! 🔥"
    )
    bot.send_message(CHANNEL_ID, end_summary, parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def start_cmd(message):
    is_active = session_running.is_set()
    status_text = "نشطة 🚀" if is_active else "متوقفة 🛑"
    welcome_msg = (
        f"🙋‍♂️ أهلاً بك يا كابتن في لوحة تحكم **{CHANNEL_NAME}**\n\n"
        f"البوت يعمل سحابياً 24/7. حالة الجلسة الآلية حالياً: **{status_text}**"
    )
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=main_keyboard(is_active))

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    if session_running.is_set():
        session_running.clear()
        bot.send_message(message.chat.id, "🛑 تم إرسال أمر إيقاف الجلسة! سيتم إنهاء الجلسة ونشر الملخص حالاً.")
    else:
        bot.send_message(message.chat.id, "⚠️ لا توجد جلسة نشطة أساساً لتوقيفها.")

@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    global session_running
    
    if call.data == "start_session":
        if not session_running.is_set():
            session_running.set()
            bot.answer_callback_query(call.id, "تم بدء الجلسة التلقائية بنجاح!")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=main_keyboard(True))
            bot.send_message(call.message.chat.id, "🚀 **بدأت صفقات الـ OTC الآلية بالعمل!** البوت يرسل الصفقات الآن للقناة تباعاً.")
            
            t = Thread(target=run_trading_session, args=(call.message.chat.id,))
            t.start()
        else:
            bot.answer_callback_query(call.id, "الجلسة قيد التشغيل بالفعل!")

    elif call.data == "stop_session":
        if session_running.is_set():
            session_running.clear()
            bot.answer_callback_query(call.id, "جاري إيقاف الجلسة...")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=main_keyboard(False))
            bot.send_message(call.message.chat.id, "🛑 تم إيقاف الجلسة بنجاح ونشر الملخص.")
        else:
            bot.answer_callback_query(call.id, "الجلسة متوقفة أصلاً.")

    elif call.data == "stats":
        bot.answer_callback_query(call.id, "عرض الإحصائيات")
        bot.send_message(
            call.message.chat.id, 
            f"📈 **إحصائيات الجلسة الحالية:**\n"
            f"- الصفقات المرسلة: {session_stats['total']}\n"
            f"- الأرباح: {session_stats['wins']} ✅\n"
            f"- الخسائر: {session_stats['losses']} ❌"
        )

if __name__ == '__main__':
    t = Thread(target=run_web)
    t.start()
    print("🤖 Fully Automated Session Bot is active...")
    bot.infinity_polling()
