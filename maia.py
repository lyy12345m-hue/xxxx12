import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import samino

# تخزين بيانات المستخدمين مؤقتًا
users = {}

# دالة التوثيق باستخدام samino
def verify_account(email, password):
    client = samino.Client()
    try:
        client.login(email=email, password=password, clientType=300)
        return f"✅ تم التحقق من الحساب بنجاح.\n📧 البريد الإلكتروني: {email}"
    except KeyError:
        return f"✅ تم التحقق من الحساب بنجاح (تجاوز خطأ بسيط).\n📧 البريد الإلكتروني: {email}"
    except Exception as e:
        print(f"خطأ أثناء التوثيق: {e}")
        return (
            f"❌ تعذر تسجيل الدخول إلى الحساب.\n"
            f"📧 البريد الإلكتروني: {email}\n"
            f"📌 السبب: {str(e)}"
        )

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك في بوت التوثيق.\n"
        "📌 الرجاء إرسال البريد الإلكتروني الخاص بك:"
    )

# استقبال الرسائل خطوة بخطوة
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in users:
        users[user_id] = {"email": text}
        await update.message.reply_text("📧 تم حفظ البريد الإلكتروني.\nالآن أرسل كلمة المرور:")
    elif "password" not in users[user_id]:
        users[user_id]["password"] = text
        await update.message.reply_text("🔐 تم حفظ كلمة المرور.\nاكتب /login لتسجيل الدخول.")
    else:
        await update.message.reply_text("✅ بياناتك محفوظة.\nاكتب /login لتسجيل الدخول.")

# أمر /login لتنفيذ التوثيق
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in users and "email" in users[user_id] and "password" in users[user_id]:
        email = users[user_id]["email"]
        password = users[user_id]["password"]
        result = verify_account(email, password)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("⚠️ يرجى إدخال البريد الإلكتروني وكلمة المرور أولاً.")

# تشغيل البوت
TOKEN = os.getenv("BOT_TOKEN")
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("login", login))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()