import os
import time
from flask import Flask
from dotenv import load_dotenv
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# ✅ تحميل المتغيرات البيئية
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# ✅ تهيئة Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running on Render!"

# ✅ تعريف وظائف البوت
async def start(update: Update, context):
    chat_type = update.message.chat.type
    if chat_type == "private":
        await update.message.reply_text("مرحبًا بك في البوت! أضفني إلى مجموعة لاستخدام ميزاتي.")
    else:
        await update.message.reply_text("تم تفعيل البوت في المجموعة ✅")

async def kick_user(update: Update, context):
    if not update.message.reply_to_message:
        await update.message.reply_text("الرجاء إعادة الرد على رسالة المستخدم")
        return
    user_id = update.message.reply_to_message.from_user.id
    chat_id = update.message.chat_id
    await context.bot.ban_chat_member(chat_id, user_id)
    await update.message.reply_text("🚫 تم حظر المستخدم")

async def pin_message(update: Update, context):
    if not update.message.reply_to_message:
        await update.message.reply_text("يجب الرد على رسالة لتثبيتها")
        return
    await update.message.reply_to_message.pin()
    await update.message.reply_text("📌 تم تثبيت الرسالة")

# ✅ نظام اكتشاف السبام
user_messages = {}

async def check_spam(update: Update, context):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    current_time = time.time()

    if user_id not in user_messages:
        user_messages[user_id] = []

    user_messages[user_id] = [t for t in user_messages[user_id] if current_time - t < 10]
    user_messages[user_id].append(current_time)

    if len(user_messages[user_id]) > 5:
        await update.message.reply_text("🚨 تحذير! لا ترسل رسائل كثيرة بسرعة.")
        await context.bot.restrict_chat_member(
            chat_id, 
            user_id, 
            permissions=ChatPermissions(can_send_messages=False), 
            until_date=current_time + 60
        )
        return

async def welcome_new_member(update: Update, context):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"🎉 مرحبًا {member.first_name} في المجموعة! 🚀")

# ✅ إعداد البوت
bot_app = Application.builder().token(TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("kick", kick_user))
bot_app.add_handler(CommandHandler("pin", pin_message))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_spam))
bot_app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

# ✅ تشغيل البوت
async def run_bot():
    print("🤖 Bot is running on Render!")
    await bot_app.run_polling()

# ✅ تشغيل Flask والبوت معًا
if __name__ == "__main__":
    from threading import Thread
    import asyncio

    # Flask app listens on PORT provided by Render
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if not set
    Thread(target=lambda: app.run(host="0.0.0.0", port=port)).start()

    # Running Telegram bot
    asyncio.run(bot_app.run_polling())
