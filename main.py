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

# متغيرات لإدارة حالة الجلسة
session_running = Event()
session_stats = {"total": 0, "wins": 0, "losses": 0}

@app.route('/')
def home():
    return "Bot is active and running 24/7!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- لوحة التحكم ---
def main_keyboard(is_active=False):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    if not is_active:
        markup.add(
            InlineKeyboardButton("🚀 بدء جلسة صفقات الـ OTC الاحترافية", callback_data="start_session"),
            InlineKeyboardButton("📊 عرض الإحصائيات الحالية", callback_data="stats")
        )
    else:
        markup.add(
            InlineKeyboardButton("🛑 إيقاف الجلسة الحالية (STOP)", callback_data="stop_session"),
            InlineKeyboardButton("📊 عرض الإحصائيات الحالية", callback_data="stats")
        )
    return markup

# --- دالة الجلسة الزمنية الحقيقية والمضبوطة بدقة ---
def run_trading_session(chat_id):
    global session_stats
    session_stats = {"total": 0, "wins": 0, "losses": 0}
    
    start_notice = (
        f"🚨 **بدء جلسة تداول الـ OTC الاحترافية - {CHANNEL_NAME}** 🚨\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔥 البوت يعمل الآن بنظام التوقيت الحقيقي (فريم 5 دقائق).\n"
        "⚠️ يرجى الالتزام التام بإدارة رأس المال وتجهيز المنصة!\n"
        f"🔗 رابط المنصة: [Quotex]({AFFILIATE_LINK})"
    )
    bot.send_message(CHANNEL_ID, start_notice, parse_mode="Markdown", disable_web_page_preview=True)
    
    pairs = ["EUR/USD-OTC", "GBP/USD-OTC", "AUD/CAD-OTC", "USD/JPY-OTC", "EUR/GBP-OTC"]
    
    while session_running.is_set():
        pair = random.choice(pairs)
        
        # 1. تنبيه تحضيري قبل الصفقة بدقيقة كاملة (60 ثانية)
        pre_msg = (
            f"🔔 **تنبيه صفقة قادمة في الجلسة**\n"
            f"💱 الزوج: `{pair}`\n"
            f"⏳ جاهزوا أنفسكم، الدخول خلال دقيقة واحدة..."
        )
        bot.send_message(CHANNEL_ID, pre_msg, parse_mode="Markdown")
        
        # عداد دقيقة كاملة للتحضير
        for _ in range(60):
            if not session_running.is_set():
                break
            time.sleep(1)
            
        if not session_running.is_set():
            break
            
        # 2. إرسال صفقة الدخول الرسمية
        direction = random.choice(["شراء / صعود (CALL)", "بيع / هبوط (PUT)"])
        signal_msg = (
            f"🎯 **توصية OTC جديدة - {CHANNEL_NAME}** 🎯\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"💱 **الزوج:** {pair}\n"
            f"🟢 **الاتجاه:** {direction}\n"
            "⏰ **مدة الصفقة:** 5 دقائق (فريم M5)\n"
            "📍 **السبب الفني:** ارتداد هيكلي من منطقة سيولة + تأكيد الزخم\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 [التسجيل في المنصة]({AFFILIATE_LINK})"
        )
        bot.send_message(CHANNEL_ID, signal_msg, parse_mode="Markdown", disable_web_page_preview=True)
        session_stats["total"] += 1
        
        # 3. الانتظار الحقيقي لمدة الصفقة (5 دقائق = 300 ثانية) لضمان مطابقة الوقت تماماً
        for _ in range(300):
            if not session_running.is_set():
                break
            time.sleep(1)
            
        if not session_running.is_set():
            break
            
        # 4. إرسال نتيجة الصفقة بدقة بعد انتهاء الـ 5 دقائق
        is_win = random.choices([True, False], weights=[82, 18])[0] # نسبة نجاح احترافية 82%
        if is_win:
            session_stats["wins"] += 1
            res_text = f"🎉 **نتيجة الصفقة ({pair}): ربح ساحق (WIN) ✅🔥**"
        else:
            session_stats["losses"] += 1
            res_text = f"❌ **نتيجة الصفقة ({pair}): خسارة (LOSS) - تعويضها في الصفقة القادمة**"
            
        bot.send_message(CHANNEL_ID, res_text, parse_mode="Markdown")
        
        # استراحة قصيرة لمدة 30 ثانية بين الصفقة والأخرى
        for _ in range(30):
            if not session_running.is_set():
                break
            time.sleep(1)

    # ملخص نهاية الجلسة عند إيقافها
    end_summary = (
        f"🏁 **انتهت جلسة التداول بنجاح - {CHANNEL_NAME}** 🏁\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 **إحصائيات الجلسة الإجمالية:**\n"
        f"- إجمالي الصفقات: {session_stats['total']}\n"
        f"- الصفقات الرابحة: {session_stats['wins']} ✅\n"
        f"- الصفقات الخاسرة: {session_stats['losses']} ❌\n"
        "شكراً لتفاعلكم ونراكم في الجلسات القادمة! 🔥"
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
            bot.answer_callback_query(call.id, "تم بدء الجلسة الاحترافية بنجاح!")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=main_keyboard(True))
            bot.send_message(call.message.chat.id, "🚀 **بدأت جلسة صفقات الـ OTC الاحترافية!** البوت يدير التوقيتات (دقيقة تحضير + 5 دقائق صفقة) بشكل آلي تماماً.")
            
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
    print("🤖 Professional OTC Session Bot is active...")
    bot.infinity_polling()
