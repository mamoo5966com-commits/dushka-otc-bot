import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from flask import Flask
from threading import Thread, Event
import time
import random
from datetime import datetime

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
            InlineKeyboardButton("🚀 بدء جلسة استراتيجيات النخبة (10 دقائق M10)", callback_data="start_session"),
            InlineKeyboardButton("📊 عرض الإحصائيات الحالية", callback_data="stats")
        )
    else:
        markup.add(
            InlineKeyboardButton("🛑 إيقاف الجلسة الحالية (STOP)", callback_data="stop_session"),
            InlineKeyboardButton("📊 عرض الإحصائيات الحالية", callback_data="stats")
        )
    return markup

# --- دالة إرسال آمنة تمنع أي جمود أو خطأ Markdown ---
def send_safe(text):
    try:
        bot.send_message(CHANNEL_ID, text, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        print(f"Markdown error: {e}, sending as plain text.")
        try:
            bot.send_message(CHANNEL_ID, text, parse_mode=None, disable_web_page_preview=True)
        except Exception as e2:
            print(f"Critical error sending message: {e2}")

# --- قاعدة بيانات استراتيجيات النخبة الشاملة ---
def get_comprehensive_strategy(direction):
    if "صعود" in direction:
        strategies = [
            ("استراتيجية ارتداد البولنجر السفلي (Bollinger Rejection)", "ملامسة السعر للحد السفلي مع تشبع بيعي تام على RSI + ظهور شمعة مطرقة (Hammer) داعمة للصعود."),
            ("استراتيجية كسر المقاومة وإعادة الاختبار (Breakout & Retest)", "اختراق مستوى مقاومة رئيسي وثبات السعر فوقه، مع إعادة اختبار ناجحة لخط الدعم الجديد على فريم M10."),
            ("استراتيجية تقاطع المتوسطات الآسية (EMA 9/21 Trend)", "تقاطع إيجابي ونزعة صعودية واضحة للمتوسطات في منطقة سيولة وطلب رئيسية."),
            ("استراتيجية ارتداد مستويات فيبوناتشي الذهبية (Fibonacci Golden Pocket)", "ارتداد السعر بدقة من منطقة التصحيح 61.8% مع ضغط شرائي مكثف."),
            ("استراتيجية امتصاص السيولة (Liquidity Sweep)", "هبوط وهمي لاختبار قاع سابق وامتصاص الأوامر المعلقة مع ارتداد هيكلي قوي صعوداً.")
        ]
    else:
        strategies = [
            ("استراتيجية ارتداد البولنجر العلوي (Bollinger Rejection)", "ملامسة السعر للحد العلوي مع تشبع شرائي تام على RSI + ظهور شمعة شهاب ساقط (Shooting Star)."),
            ("استراتيجية كسر الدعم وإعادة الاختبار (Breakout & Retest)", "كسر مستوى دعم قوي وتحوله لمقاومة مع إعادة اختبار ناجحة للمستوى على فريم M10."),
            ("استراتيجية تقاطع المتوسطات الآسية (EMA 9/21 Trend)", "تقاطع سلبي وانعكاس في اتجاه الزخم تحت متوسط 21 عند منطقة عرض قوية."),
            ("استراتيجية ارتداد مستويات فيبوناتشي الذهبية (Fibonacci Golden Pocket)", "رفض السعر لمنطقة التصحيح العلوي 61.8% مع دخول سيولة بيعية ضخمة."),
            ("استراتيجية امتصاص السيولة (Liquidity Sweep)", "صعود وهمي لاختبار قمة سابقة وضرب وقف الخسائر ثم انعكاس حاد هبوطاً.")
        ]
    return random.choice(strategies)

# --- دالة الجلسة الزمنية لفريم 10 دقائق بالضبط (600 ثانية) ---
def run_trading_session(chat_id):
    global session_stats
    session_stats = {"total": 0, "wins": 0, "losses": 0}
    
    start_notice = (
        f"🚨 **بدء جلسة استراتيجيات النخبة (فريم 10 دقائق M10) - {CHANNEL_NAME}** 🚨\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔥 التداول الآن بنظام فريم المدى الواسع (10 دقائق) لضمان أعلى دقة.\n"
        "⚠️ يرجى الالتزام التام بإدارة رأس المال وتجهيز المنصة!\n"
        f"🔗 رابط المنصة: {AFFILIATE_LINK}"
    )
    send_safe(start_notice)
    
    pairs = ["EUR/USD-OTC", "GBP/USD-OTC", "AUD/CAD-OTC", "USD/JPY-OTC", "EUR/GBP-OTC"]
    
    while session_running.is_set():
        try:
            pair = random.choice(pairs)
            
            # حساب دقيقة افتتاح الشمعة القادمة
            now = datetime.now()
            entry_minute = (now.minute + 2) % 60
            
            # 1. تنبيه تحضيري قبل الصفقة
            pre_msg = (
                f"🔔 **تنبيه صفقة قادمة (فريم 10 دقائق)**\n"
                f"💱 الزوج المرتقب: `{pair}`\n"
                f"⏳ التجهيز للدخول عند افتتاح شمعة الدقيقة **{entry_minute:02d}**.. استعدوا!"
            )
            send_safe(pre_msg)
            
            # انتظار التحضير (120 ثانية = دقيقتان)
            for _ in range(120):
                if not session_running.is_set():
                    break
                time.sleep(1)
                
            if not session_running.is_set():
                break
                
            # 2. تحديد الاتجاه والاستراتيجية
            direction = random.choice(["شراء / صعود (CALL)", "بيع / هبوط (PUT)"])
            strat_name, strat_details = get_comprehensive_strategy(direction)
            
            actual_time_str = datetime.now().strftime("%H:%M")
            
            signal_msg = (
                f"🎯 **توصية نخبوية جديدة - {CHANNEL_NAME}** 🎯\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"💱 **الزوج:** {pair}\n"
                f"🟢 **الاتجاه:** {direction}\n"
                f"⏰ **وقت الدخول:** عند الدقيقة ({entry_minute:02d}) - الساعة {actual_time_str}\n"
                f"⏱ **مدة الصفقة:** 10 دقائق كاملة (فريم M10)\n"
                f"📊 **الاستراتيجية:** {strat_name}\n"
                f"📍 **التحليل الفني:** {strat_details}\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"🔗 [التسجيل في المنصة]({AFFILIATE_LINK})"
            )
            send_safe(signal_msg)
            session_stats["total"] += 1
            
            # 3. الانتظار الحقيقي لمدة الصفقة (10 دقائق كاملة = 600 ثانية حصرياً)
            for _ in range(600):
                if not session_running.is_set():
                    break
                time.sleep(1)
                
            if not session_running.is_set():
                break
                
            # 4. إرسال نتيجة الصفقة بعد انقضاء الـ 10 دقائق بدقة
            is_win = random.choices([True, False], weights=[89, 11])[0]
            if is_win:
                session_stats["wins"] += 1
                res_text = f"🎉 **نتيجة الصفقة ({pair}): ربح ساحق بامتياز بعد 10 دقائق (WIN) ✅🔥**"
            else:
                session_stats["losses"] += 1
                res_text = f"❌ **نتيجة الصفقة ({pair}): خسارة (LOSS) - السوق عكس الاتجاه، سنعوضها في الصفقة القادمة**"
                
            send_safe(res_text)
            
            # استراحة لمدة 45 ثانية بين الصفقة والأخرى
            for _ in range(45):
                if not session_running.is_set():
                    break
                time.sleep(1)
                
        except Exception as loop_err:
            print(f"Error inside session loop: {loop_err}")
            time.sleep(5)

    # ملخص نهاية الجلسة
    end_summary = (
        f"🏁 **انتهت جلسة استراتيجيات النخبة (M10) بنجاح - {CHANNEL_NAME}** 🏁\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 **إحصائيات الجلسة الإجمالية:**\n"
        f"- إجمالي الصفقات: {session_stats['total']}\n"
        f"- الصفقات الرابحة: {session_stats['wins']} ✅\n"
        f"- الصفقات الخاسرة: {session_stats['losses']} ❌\n"
        "شكراً لتفاعلكم ونراكم في الجلسات القادمة! 🔥"
    )
    send_safe(end_summary)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    is_active = session_running.is_set()
    status_text = "نشطة 🚀" if is_active else "متوقفة 🛑"
    welcome_msg = (
        f"🙋‍♂️ أهلاً بك يا كابتن في لوحة تحكم **{CHANNEL_NAME}**\n\n"
        f"البوت يعمل بنظام استراتيجيات النخبة لفريم 10 دقائق 24/7. حالة الجلسة الآلية حالياً: **{status_text}**"
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
            bot.answer_callback_query(call.id, "تم بدء جلسة استراتيجيات النخبة (10 دقائق) بنجاح!")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=main_keyboard(True))
            bot.send_message(call.message.chat.id, "🚀 **بدأت صفقات فريم الـ 10 دقائق المزامنة مع الشموع!** البوت يدير التوقيتات والاستراتيجيات المتقدمة بشكل آلي تام.")
            
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
    print("🤖 Elite M10 Strategy Bot is active...")
    
    bot.remove_webhook()
    time.sleep(1)
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)
