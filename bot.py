from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import time


TOKEN = "7537226110:AAEiwFnCn3T7B4BJZ1-bx7QxDDmZ9twLpEc"

async def start(update: Update, context):
    chat_type = update.message.chat.type
    if chat_type == "private":
        await update.message.reply_text("مرحبًا بك في البوت! أضفني إلى مجموعة لاستخدام ميزاتي.")
    else:
        await update.message.reply_text("تم تفعيل البوت في المجموعة ✅")

# ##############################################
async def kick_user(update: Update, context):
    if not update.message.reply_to_message:
        await update.message.reply_text("الرجاء إعادة الرد على رسالة المستخدم")
        return
    user_id = update.message.reply_to_message.from_user.id
    chat_id = update.message.chat_id
    await context.bot.ban_chat_member(chat_id,user_id)
    await update.message.reply_text("block")

##################################################
async def pin_message(update: Update,context):
    if not update.message.reply_to_message:
        await update.message.reply_text(" يجب الرد على رسالة لتثبيتها")
        return
    await update.message.reply_to_message.pin()
    await update.message.reply_text("تم تثبيت الرسالة")

    ##################################################

    # سجل المستخدمين
user_messages = {}

async def check_spam(update: Update, context):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    current_time = time.time()

    # تحقق إذا كان المستخدم جديدًا
    if user_id not in user_messages:
        user_messages[user_id] = []

    # إزالة الرسائل القديمة (أكثر من 10 ثوانٍ)
    user_messages[user_id] = [t for t in user_messages[user_id] if current_time - t < 10]

    # إضافة الوقت الحالي إلى سجل المستخدم
    user_messages[user_id].append(current_time)

    # إذا تجاوز عدد الرسائل المسموح به، قم بحظره مؤقتًا
    if len(user_messages[user_id]) > 5:  # يسمح بـ 5 رسائل كل 10 ثوانٍ
        await update.message.reply_text("🚨 تحذير! لا ترسل رسائل كثيرة بسرعة.")
        await context.bot.restrict_chat_member(chat_id, user_id, permissions={"can_send_messages": False}, until_date=current_time + 60)
        return
    ############################################################
async def welcome_new_member(update: Update, context):
   for member in update.message.new_chat_members:
        await update.message.reply_text(f"🎉 مرحبًا {member.first_name} في المجموعة! 🚀")
        return
   #######################################################


def main():
    app = Application.builder().token(TOKEN).build()

    # إضافة أوامر البوت
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kick", kick_user))
    app.add_handler(CommandHandler("pin", pin_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_spam))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

    print("البوت يعمل الآن 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
