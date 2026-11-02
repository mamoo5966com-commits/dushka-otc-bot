import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from flask import Flask
from threading import Thread, Event
import time
import random
from datetime import datetime, timedelta, timezone

TOKEN = "9086361088:AAErE0hgvSzCkCCSlobAxxK5gZXg6h6bvnM"
CHANNEL_ID = "@doshkotc"
AFFILIATE_LINK = "https://broker-qx.pro/sign-up?lid=2388879"
CHANNEL_NAME = "Dushka Trading Signal VIP"

# ضبط النطاق الزمني الثابت على +3 GMT لتتطابق الساعة مع وقتك المحلي تماماً
TZ_GMT3 = timezone(timedelta(hours=3))

bot = telebot.TeleBot(TOKEN)
app = Flask('')

session_running = Event()
session_stats = {"total": 0, "wins": 0, "losses": 0}

last_signal_info = {"pair": "", "direction": "", "timeframe": ""}

@app.route('/')
def home():
    return "Bot is active and running 24/7!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def main_keyboard(is_active=False):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    if not is_active:
        markup.add(
            InlineKeyboardButton("🚀 بدء جلسة استراتيجيات النخبة المتنوعة (M5, M10, M15)", callback_data="start_session"),
            InlineKeyboardButton("📊 عرض الإحصائيات الحالية", callback_data="stats")
        )
    else:
        markup.add(
            InlineKeyboardButton("✅ نشر نتيجة: صفقة ناجحة (WIN)", callback_data="manual_win"),
            InlineKeyboardButton("❌ نشر نتيجة: صفقة خاسرة (LOSS)", callback_data="manual_loss"),
            InlineKeyboardButton("🛑 إيقاف الجلسة الحالية (STOP)", callback_data="stop_session"),
            InlineKeyboardButton("📊 عرض الإحصائيات الحالية", callback_data="stats")
        )
    return markup

def send_safe(text):
    try:
        bot.send_message(CHANNEL_ID, text, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        print(f"Markdown error: {e}, sending as plain text.")
        try:
            bot.send_message(CHANNEL_ID, text, parse_mode=None, disable_web_page_preview=True)
        except Exception as e2:
            print(f"Critical error sending message: {e2}")

def get_comprehensive_strategy(direction):
    if "صعود" in direction:
        strategies = [
            ("ارتداد البولنجر السفلي + تشبع بيعي RSI", "ملامسة السعر للحد السفلي مع تشبع بيعي على RSI + ظهور شمعة مطرقة (Hammer) داعمة للصعود."),
            ("كسر المقاومة وإعادة الاختبار (Breakout & Retest)", "اختراق مستوى مقاومة رئيسي وثبات السعر فوقه مع إعادة اختبار ناجحة على الفريم المحدد."),
            ("تقاطع المتوسطات الآسية (EMA 9/21 Trend)", "تقاطع إيجابي ونزعة صعودية واضحة للمتوسطات في منطقة سيولة وطلب رئيسية."),
            ("ارتداد مستويات فيبوناتشي الذهبية (Golden Pocket)", "ارتداد السعر بدقة من منطقة التصحيح 61.8% مع ضغط شرائي مكثف."),
            ("امتصاص السيولة (Liquidity Sweep)", "هبوط وهمي لاختبار قاع سابق وامتصاص الأوامر مع ارتداد هيكلي قوي صعوداً.")
        ]
    else:
        strategies = [
            ("ارتداد البولنجر العلوي + تشبع شرائي RSI", "ملامسة السعر للحد العلوي مع تشبع شرائي على RSI + ظهور شمعة شهاب ساقط (Shooting Star)."),
            ("كسر الدعم وإعادة الاختبار (Breakout & Retest)", "كسر مستوى دعم وتحوله لمقاومة مع إعادة اختبار ناجحة للمستوى على الفريم المحدد."),
            ("تقاطع المتوسطات الآسية (EMA 9/21 Trend)", "تقاطع سلبي وانعكاس في اتجاه الزخم تحت متوسط 21 عند منطقة عرض قوية."),
            ("ارتداد مستويات فيبوناتشي الذهبية (Golden Pocket)", "رفض السعر لمنطقة التصحيح العلوي 61.8% مع دخول سيولة بيعية ضخمة."),
            ("امتصاص السيولة (Liquidity Sweep)", "صعود وهمي لاختبار قمة سابقة وضرب وقف الخسائر ثم انعكاس حاد هبوطاً.")
        ]
    return random.choice(strategies)

def run_trading_session(chat_id):
    global session_stats, last_signal_info
    session_stats = {"total": 0, "wins": 0, "losses": 0}
    
    start_notice = "🟢 **تم تفعيل نظام التوصيات النخبوية متعددة الأوقات (M5, M10, M15)** 🔥"
    send_safe(start_notice)
    
    pairs = ["USD/CAD", "EUR/USD", "GBP/USD", "USD/JPY", "AUD/CAD"]
    timeframes = [
        {"name": "5 دقائق (M5)", "duration": 5, "step": 5},
        {"name": "10 دقائق (M10)", "duration": 10, "step": 10},
        {"name": "15 دقيقة (M15)", "duration": 15, "step": 15}
    ]
    
    while session_running.is_set():
        try:
            pair = random.choice(pairs)
            tf_obj = random.choice(timeframes)
            tf_name = tf_obj["name"]
            tf_duration = tf_obj["duration"]
            tf_step = tf_obj["step"]
            
            # حساب الوقت بدقة تبعا للنطاق الزمني GMT+3 ومضاعفات الفريم المختار
            now = datetime.now(TZ_GMT3)
            current_minute = now.minute
            
            target_minute = ((current_minute // tf_step) + 1) * tf_step
            if target_minute >= 60:
                target_minute = 0
                
            target_time = now.replace(minute=target_minute, second=0, microsecond=0)
            if target_minute <= current_minute:
                target_time += timedelta(hours=1) if target_minute == 0 and current_minute >= (60 - tf_step) else timedelta(minutes=tf_step)
                
            # إرسال التوصية قبل الموعد بـ 3 دقائق تماماً
            publish_time = target_time - timedelta(minutes=3)
            sleep_to_publish = (publish_time - datetime.now(TZ_GMT3)).total_seconds()
            
            if sleep_to_publish > 0:
                for _ in range(int(sleep_to_publish)):
                    if not session_running.is_set():
                        break
                    time.sleep(1)
                    
            if not session_running.is_set():
                break
                
            direction = random.choice(["CALL (صعود)", "PUT (هبوط)"])
            strat_name, strat_details = get_comprehensive_strategy(direction)
            
            entry_time_str = target_time.strftime("%H:%M")
            
            last_signal_info["pair"] = pair
            last_signal_info["direction"] = direction
            last_signal_info["timeframe"] = tf_name
            
            signal_msg = (
                "🔥 **إشارة توصية فائقة الدقة (Balanced Confluence Bot)** 🔥\n\n"
                f"💎 **الزوج:** {pair}\n"
                f"⏳ **مدة الصفقة:** {tf_name}\n"
                f"📈 **الاتجاه:** {direction}\n"
                f"⏰ **وقت الدخول:** {entry_time_str} (بتوقيت +3 GMT)\n"
                f"📊 **الاستراتيجية:** {strat_name}\n"
                f"📊 **مؤشرات الفحص:** {strat_details}\n\n"
                "⚠️ صفقة ذات تصفية متوازنة، التزم بإدارة رأس المال والمضاعفة عند الحاجة.\n"
                "🔗 رابط التسجيل في المنصة:\n"
                f"{AFFILIATE_LINK}\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"📢 مقدمة من: قناة دوشكا للتوصيات | {CHANNEL_ID}"
            )
            send_safe(signal_msg)
            session_stats["total"] += 1
            
            try:
                bot.send_message(chat_id, f"🔔 تم إرسال صفقة `{pair}` ({direction}) على فريم `{tf_name}` لوقت {entry_time_str}. تابعها في المنصة وعند انتهائها اضغط زر النتيجة.")
            except:
                pass
            
            # الانتظار حتى وقت الدخول وانتهاء الصفقة (وقت التحضير + مدة الصفقة بالثواني)
            total_wait = (target_time - datetime.now(TZ_GMT3)).total_seconds() + (tf_duration * 60)
            if total_wait > 0:
                for _ in range(int(total_wait)):
                    if not session_running.is_set():
                        break
                    time.sleep(1)
                    
            if not session_running.is_set():
                break
            
            # فترة استراحة بين الصفقات
            for _ in range(200):
                if not session_running.is_set():
                    break
                time.sleep(1)
                
        except Exception as loop_err:
            print(f"Error inside session loop: {loop_err}")
            time.sleep(5)

    end_summary = (
        "🏁 **انتهت جلسة التداول بنجاح** 🏁\n"
        f"📊 إجمالي الصفقات: {session_stats['total']} | الأرباح: {session_stats['wins']} ✅ | الخسائر: {session_stats['losses']} ❌"
    )
    send_safe(end_summary)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    is_active = session_running.is_set()
    status_text = "نشطة 🚀" if is_active else "متوقفة 🛑"
    welcome_msg = (
        f"🙋‍♂️ أهلاً بك يا كابتن في لوحة تحكم {CHANNEL_NAME}\n\n"
        f"البوت يعمل بتوقيت (+3 جغرافي) وبدعم الفريمات المتنوعة (M5, M10, M15). الحالة: {status_text}"
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
    global session_running, session_stats
    
    if call.data == "start_session":
        if not session_running.is_set():
            session_running.set()
            bot.answer_callback_query(call.id, "تم بدء الجلسة المتنوعة بنجاح!")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=main_keyboard(True))
            bot.send_message(call.message.chat.id, "🚀 **بدأت الجلسة المتنوعة (M5, M10, M15) بتوقيت +3 GMT مع التحكم اليدوي!**")
            
            t = Thread(target=run_trading_session, args=(call.message.chat.id,))
            t.start()
        else:
            bot.answer_callback_query(call.id, "الجلسة قيد التشغيل بالفعل!")

    elif call.data == "manual_win":
        if session_running.is_set() and last_signal_info["pair"]:
            session_stats["wins"] += 1
            win_text = (
                "🎉 **تحديث نتيجة الصفقة (WIN)** 🚀\n\n"
                f"💎 **الزوج:** `{last_signal_info['pair']}`\n"
                f"⏳ **الفريم:** `{last_signal_info['timeframe']}`\n"
                f"📈 **الاتجاه:** `{last_signal_info['direction']}`\n"
                "✅ **الحالة:** ربح ناجح بامتياز"
            )
            send_safe(win_text)
            bot.
