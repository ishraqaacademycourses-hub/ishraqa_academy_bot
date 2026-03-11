import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ChatMemberHandler
import logging
from datetime import datetime
import re
import json
import os
from flask import Flask, request

# -------------------- إعدادات التسجيل --------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------------------- إعدادات البوت --------------------
class Config:
    TOKEN = "8630466238:AAEjK9Bf7w95NtDUqQSyvTn19Q9AzP1u2pc"
    SHEET_NAME = "IS Register"
    MARKETERS_SHEET = "Marketers"
    DASHBOARD_SHEET = "Marketers Dashboard"
    CREDENTIALS_FILE = "marketers-code112-40ca97e9593c.json"  # هترفع الملف ده برضه
    
    # الروابط
    REGISTER_LINK = "https://docs.google.com/forms/d/e/1FAIpQLScCAz01QmYN1F5JvMTF7TQuPV-P55Xeyy6vC65msOv7bnsSXA/viewform?usp=sharing&ouid=112261112014561319884939"
    STUDENT_REGISTER_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSfFQrE9qCtaYMlfiTfVaWYNcZmXzL9n0Aj5r-sIPwNydg67dw/viewform"
    
    KEYWORDS_FOR_CODE = ["كود", "اعرف الكود", "كود المسوق", "الكود", "code"]
    
    ANNOUNCEMENTS_CHANNEL = "https://t.me/ishraqaacademymarketers"
    MARKETERS_GROUP = "https://t.me/ishraqaacademymarketerschat"
    RESULTS_CHANNEL = "https://t.me/ishraqaacademycommunity"
    BOT_USERNAME = "IshraqaMarketersBot"
    
    ADMIN_IDS = []
    
    # ⚠️ مهم: استبدل USERNAME باسم المستخدم بتاعك في PythonAnywhere
    PA_USERNAME = "yourusername"  # غير ده لاسم المستخدم بتاعك
    WEBHOOK_URL = f"https://{PA_USERNAME}.pythonanywhere.com/webhook"

# -------------------- باقي الكود (BadgeSystem, SheetsManager, UserManager, BotHandlers) --------------------
# هنا تحط كل الكود اللي انت كاتبه من قبل، زي ما هو تماماً
# (محتوى BotHandlers كامل من الكود السابق)

# -------------------- إعداد Flask للـ Webhook --------------------
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """استقبال التحديثات من Telegram عبر Webhook"""
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return 'OK', 200

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """تثبيت Webhook (استخدمها مرة واحدة)"""
    webhook_url = f"https://{Config.PA_USERNAME}.pythonanywhere.com/webhook"
    success = application.bot.set_webhook(url=webhook_url)
    if success:
        return f"✅ Webhook set to {webhook_url}"
    return "❌ Failed to set webhook"

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return "🤖 Bot is running!"

# -------------------- إعداد التطبيق --------------------
application = Application.builder().token(Config.TOKEN).build()
handlers = BotHandlers()

# إضافة المعالجات
application.add_handler(CommandHandler("start", handlers.start))
application.add_handler(CommandHandler("help", handlers.help_command))
application.add_handler(CommandHandler("register", handlers.register_command))
application.add_handler(CommandHandler("register_student", handlers.register_student_command))
application.add_handler(CommandHandler("leaderboard", handlers.leaderboard_command))
application.add_handler(CommandHandler("profile", handlers.profile_command))
application.add_handler(CommandHandler("rank", handlers.rank_command))
application.add_handler(CommandHandler("rewards", handlers.rewards_command))
application.add_handler(CommandHandler("badges", handlers.badges_command))
application.add_handler(CommandHandler("weekly", handlers.weekly_leaderboard))
application.add_handler(CommandHandler("monthly", handlers.monthly_leaderboard))
application.add_handler(CommandHandler("channels", handlers.channels_command))

# إضافة معالج الأعضاء الجدد
application.add_handler(ChatMemberHandler(
    handlers.welcome_new_member, 
    ChatMemberHandler.CHAT_MEMBER
))

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message))
application.add_handler(CallbackQueryHandler(handlers.handle_callback))

# -------------------- دالة register_student_command --------------------
# أضفها في كلاس BotHandlers
async def register_student_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎓 اضغط لتسجيل طالب جديد", url=Config.STUDENT_REGISTER_LINK)],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📝 **تسجيل طالب جديد**\n\n"
        "استخدم هذا الرابط لتسجيل طالب جديد:\n"
        "• املأ جميع البيانات المطلوبة\n"
        "• ارفع صورة إثبات الدفع\n"
        "• تأكد من إدخال كود المسوق الخاص بك\n\n"
        "✅ بعد الإرسال، سيتم احتساب التسجيل في رصيدك فوراً!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# -------------------- تشغيل التطبيق --------------------
if __name__ == '__main__':
    # شغل Flask app (هيتعامل معاه PythonAnywhere تلقائياً)
    app.run()