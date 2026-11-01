import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from flask import Flask
from threading import Thread
import time

# بيانات البوت والقناة التجريبية ورابط الأفلييت الخاص بك
TOKEN = "9086361088:AAErE0hgvSzCkCCSlobAxxK5gZXg6h6bvnM"
CHANNEL_ID = "@doshkotc"
AFFILIATE_LINK = "https://quotex.com"  # استبدله برابط الأفلييت الخاص بك إذا أردت
CHANNEL_NAME = "Dushka Trading VIP"

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
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("🚨 1. إرسال تنبيه مسبق (تجهيز الصفقة)", callback_data="pre_alert"),
        InlineKeyboardButton("🚀 2. إرسال صفقة الدخول الآن (OTC)", callback_data="send_signal"),
        InlineKeyboardButton("📊 عرض إحصائيات الجلسة", callback_data="stats")
    )
    return markup

# --- لوحة تقييم نتيجة الصفقة ---
def result_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("✅ ربح (WIN)", callback_data="result_win"),
        InlineKeyboardButton("❌ خسارة (LOSS)", callback_data="result_loss")
    )
    return markup

# --- أمر التشغيل /start ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_msg = (
        f"🙋‍♂️ أهلاً بك يا كابتن في لوحة تحكم **{CHANNEL_NAME}**\n\n"
        f"البوت يعمل الآن **سحابياً 24/7** ومتصل بقناتك: `{CHANNEL_ID}`\n"
        f"اختر من القائمة أدناه لإدارة الجلسات وإرسال الإشارات:"
    )
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=main_keyboard())

# --- معالجة الأزرار التفاعلية ---
@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    if call.data == "pre_alert":
        bot.answer_callback_query(call.id, "إرسال تنبيه التحضير للصفقة...")
        alert_msg = (
            f"🚨 **تنبيه صفقة قادمة - {CHANNEL_NAME}** 🚨\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💱 **الزوج:** EUR/USD-OTC\n"
            "⏰ **الوقت:** خلال 3 دقائق تقريباً\n"
            "prepared تجهّزوا يا شباب، حضروا منصة Quotex وخليكم مستعدين للإشارة القادمة! 🔥"
        )
        try:
            bot.send_message(CHANNEL_ID, alert_msg, parse_mode="Markdown")
            bot.send_message(call.message.chat.id, "✅ تم إرسال تنبيه التحضير للقناة بنجاح!")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ خطأ: {e}")

    elif call.data == "send_signal":
        bot.answer_callback_query(call.id, "جاري إرسال التوصية الرسمية...")
        
        signal_template = (
            f"🎯 **توصية OTC جديدة - {CHANNEL_NAME}** 🎯\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💱 **الزوج:** EUR/USD-OTC\n"
            "🟢 **الاتجاه:** شراء / صعود (CALL)\n"
            "⏰ **مدة الصفقة:** 5 دقائق (فريم M5)\n"
            "📍 **السبب الفني:** ارتداد من دعم قوي + إعادة اختبار كسر المقاومة\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ *التزم بإدارة رأس المال (1-3% كحدสูงสุด).* \n"
            f"🔗 **رابط التسجيل والمنصة:** [اضغط هنا للإنضمام والبدء]({AFFILIATE_LINK})"
        )
        
        try:
            bot.send_message(CHANNEL_ID, signal_template, parse_mode="Markdown", disable_web_page_preview=True)
            # إرسال رسالة للمشرف مع أزرار النتيجة لتحديد هل ربحت أم خسرت الصفقة
            bot.send_message(call.message.chat.id, "✅ تم نشر إشارة الدخول بنجاح! حدد نتيجة الصفقة بعد انتهائها:", reply_markup=result_keyboard())
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ حدث خطأ أثناء الإرسال!\nالخطأ: {e}")

    elif call.data == "result_win":
        bot.answer_callback_query(call.id, "تم تسجيل النتيجة: ربح")
        win_msg = "🎉 **مبروك للجميع! الصفقة انتهت بربح ساحق (WIN) ✅🔥**"
        bot.send_message(CHANNEL_ID, win_msg, parse_mode="Markdown")
        bot.send_message(call.message.chat.id, "📈 تم نشر نتيجة (ربح) في القناة بنجاح.")

    elif call.data == "result_loss":
        bot.answer_callback_query(call.id, "تم تسجيل النتيجة: خسارة")
        loss_msg = "⚠️ **للأسف الصفقة انتهت بخسارة (LOSS) ❌ (نعوضها في الجلسة القادمة بإذن الله)**"
        bot.send_message(CHANNEL_ID, loss_msg, parse_mode="Markdown")
        bot.send_message(call.message.chat.id, "📉 تم نشر نتيجة (خسارة) في القناة.")

    elif call.data == "stats":
        bot.answer_callback_query(call.id, "عرض الإحصائيات")
        bot.send_message(call.message.chat.id, f"📈 **إحصائيات قناة {CHANNEL_NAME}:**\n- إجمالي صفقات اليوم: 5\n- الصفقات الناجحة: 4 ✅\n- الصفقات الخاسرة: 1 ❌\n- نسبة الدقة: 80%")

if __name__ == '__main__':
    t = Thread(target=run_web)
    t.start()
    print("🤖 Cloud OTC Bot with Full Features is active...")
    bot.infinity_polling()
