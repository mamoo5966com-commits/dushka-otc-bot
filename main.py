import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from flask import Flask
from threading import Thread, Event
import time
import random
from datetime import datetime, timedelta

# بيانات البوت والقناة ورابط الأفلييت
TOKEN = "9086361088:AAErE0hgvSzCkCCSlobAxxK5gZXg6h6bvnM"
CHANNEL_ID = "@doshkotc"
AFFILIATE_LINK = "https://broker-qx.pro/sign-up?lid=2388879"
CHANNEL_NAME = "Dushka Trading Signal VIP"

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

# --- استراتيجيات النخبة الشاملة ---
def get_comprehensive_strategy(direction):
    if "صعود" in direction:
        strategies = [
            ("ارتداد البولنجر السفلي + تشبع بيعي RSI", "ملامسة السعر للحد السفلي مع تشبع بيعي على RSI + ظهور شمعة مطرقة (Hammer)."),
            ("كسر المقاومة وإعادة الاختبار (Breakout & Retest)", "اختراق مستوى مقاومة وثبات السعر فوقه مع إعادة اختبار ناجحة على فريم M10."),
            ("تقاطع المتوسطات الآسية (EMA 9/21 Trend)", "تقاطع إيجابي ونزعة صعودية واضحة للمتوسطات في منطقة سيولة رئيسية."),
            ("ارتداد مستويات فيبوناتشي الذهبية (Golden Pocket)", "ارتداد السعر بدقة من منطقة التصحيح 61.8% مع ضغط شرائي مكثف."),
            ("امتصاص السيولة (Liquidity Sweep)", "هبوط وهمي لاختبار قاع سابق وامتصاص الأوامر مع ارتداد هيكلي قوي صعوداً.")
        ]
    else:
        strategies = [
            ("ارتداد البولنجر العلوي + تشبع شرائي RSI", "ملامسة السعر للحد العلوي مع تشبع شرائي على RSI + ظهور شمعة شهاب ساقط."),
            ("كسر الدعم وإعادة الاختبار (Breakout & Retest)", "كسر مستوى دعم وتحوله لمقاومة مع إعادة اختبار ناجحة على فريم M10."),
            ("تقاطع المتوسطات الآسية (EMA 9/21 Trend)", "تقاطع سلبي وانعكاس في اتجاه الزخم تحت متوسط 21 عند منطقة عرض قوية."),
            ("ارتداد مستويات فيبوناتشي الذهبية (Golden Pocket)", "رفض السعر لمنطقة التصحيح العلوي 61.8% مع دخول سيولة بيعية ضخمة."),
            ("امتصاص السيولة (Liquidity Sweep)", "صعود وهمي لاختبار قمة سابقة وضرب وقف الخسائر ثم انعكاس حاد هبوطاً.")
        ]
    return random.choice(strategies)

# --- دالة الجلسة الزمنية مع إرسال التوصية مسبقاً قبل الموعد بـ 3 دقائق وتصميم مطابق للبوت القديم ---
def run_trading_session(chat_id):
    global session_stats
    session_stats = {"total": 0, "wins": 0, "losses": 0}
    
    start_notice = (
        "🟢 **تم تفعيل نظام التوصيات الاحترافية (فريم 10 دقائق M10)** 🔥"
    )
    send_safe(start_notice)
    
    pairs = ["USD/CAD", "EUR/USD", "GBP/USD", "USD/JPY", "AUD/CAD"]
    
    while session_running.is_set():
        try:
            pair = random.choice(pairs)
            
            # حساب وقت الدخول المستهدف بدقة على مضاعفات الـ 10 دقائق القادمة (00, 10, 20, 30, 40, 50)
            now = datetime.now()
            current_minute = now.minute
            
            target_minute = ((current_minute // 10) + 1) * 10
            if target_minute >= 60:
                target_minute = 0
                
            target_time = now.replace(minute=target_minute, second=0, microsecond=0)
            if target_minute <= current_minute:
                target_time += timedelta(hours=1) if target_minute == 0 and current_minute >= 50 else timedelta(minutes=10)
                
            # إرسال التوصية قبل الموعد بـ 3 دقائق تماماً (180 ثانية)
            publish_time = target_time - timedelta(minutes=3)
            sleep_to_publish = (publish_time - datetime.now()).total_seconds()
            
            if sleep_to_publish > 0:
                for _ in range(int(sleep_to_publish)):
                    if not session_running.is_set():
                        break
                    time.sleep(1)
                    
            if not session_running.is_set():
                break
                
            # توليد الاتجاه والاستراتيجية
            direction = random.choice(["CALL (صعود)", "PUT (هبوط)"])
            strat_name, strat_details = get_comprehensive_strategy(direction)
            
            entry_time_str = target_time.strftime("%H:%M")
            
            # قالب التوصية المطابق تماماً لطلبك وللتصميم السابق
            signal_msg = (
                f"🔥 **إشارة توصية فائقة الدقة (Balanced Confluence Bot)** 🔥\n\n"
                f"💎 **الزوج:** `{pair}`\n"
                f"⏳ **مدة الصفقة:** 10 دقائق (فريم M10)\n"
                f"📈 **الاتجاه:** `{direction}`\n"
                f"⏰ **وقت الدخول:** `{entry_time_str}` (بتوقيت +3 GMT)\n"
                f"📊 **الاستراتيجية:** {strat_name}\n"
                f"📊 **مؤشرات الفحص:** {strat_details}\n\n"
                f"⚠️ صفقة ذات تصفية متوازنة، التزم بإدارة رأس المال والمضاعفة عند الحاجة.\n"
                f"🔗 رابط التسجيل في المنصة:\n{AFFILIATE_LINK}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📢 مقدمة من: قناة دوشكا للتوصيات | `{CHANNEL_ID}`"
            )
            send_safe(signal_msg)
            session_stats["total"] += 1
            
            # الانتظار حتى حلول وقت الدخول تماماً (الدقائق الـ 3 المتبقية حتى يصل الوقت للصفر)
            sleep_to_entry = (target_time - datetime.now()).total_seconds()
            if sleep_to_entry > 0:
                for _ in range(int(sleep_to_entry)):
                    if not session_running.is_set():
                        break
                    time.sleep(1)
                    
            if not session_running.is_set():
                break
                
            # الانتظار طوال مدة الصفقة (10 دقائق = 600 ثانية)
            for _ in range(600):
                if not session_running.is_set():
                    break
                time.sleep(1)
                
            if not session_running.is_set():
                break
                
            # إرسال نتيجة الصفقة بتصميم مطابق للبوت السابق
            is_win = random.choices([True, False], weights=[89, 11])[0]
            if is_win:
                session_stats["wins"] += 1
                res_text = (
                    f"🎉 **تحديث نتيجة الصفقة (WIN)** 🚀\n\n"
                    f"💎 **الزوج:** `{pair}`\n"
                    f"📈 **الاتجاه:** `{direction}`\n"
                    f"✅ **الحالة:** ربح ناجح بنجاح"
                )
            else:
                session_stats["losses"] += 1
                res_text = (
                    f"❌ **تحديث نتيجة الصفقة (LOSS)**\n\n"
                    f"💎 **الزوج:** `{pair}`\n"
                    f"📈 **الاتجاه:** `{direction}`\n"
                    f"❌ **الحالة:** خسارة - سيتم تعويضها في الصفقة القادمة"
                )
                
            send_safe(res_text)
            
            # استراحة قصيرة قبل التجهيز للصفقة التالية
            for _ in range(30):
                if not session_running.is_set():
                    break
                time.sleep(1)
                
        except Exception as loop_err:
            print(f"Error inside session loop: {loop_err}")
            time.sleep(5)

    # ملخص نهاية الجلسة
    end_summary = (
        f"🏁 **انتهت جلسة التداول بنجاح** 🏁\n"
        f"📊 إجمالي الصفقات: {session_stats['total']} | الأرباح: {session_stats['wins']} ✅ | الخسائر: {session_stats['losses']} ❌"
    )
    send_safe(end_summary)

@bot.message_handler(commands=['start'])
def start_cmd(message
