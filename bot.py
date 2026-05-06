import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
DATA_FILE = "vending_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"expenses":[],"incomes":[],"machines":[{"name":"מכונה 1","status":"תקינה"}]}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def start(update, ctx):
    await update.message.reply_text("👋 שלום!\n\nשלח לי:\n💸 הוצ 200 תחזוקה\n💰 הכנ 500 מכונה1\n📊 סיכום\n🔧 מכונה1 תקלה")

async def handle(update, ctx):
    text = update.message.text.strip()
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    month = datetime.now().strftime("%Y-%m")

    if text.startswith("הוצ"):
        parts = text.split()
        amount = next((p for p in parts if p.isdigit()), None)
        if amount:
            note = " ".join(parts[2:]) if len(parts) > 2 else ""
            data["expenses"].append({"amount":int(amount),"note":note,"date":today})
            save_data(data)
            await update.message.reply_text(f"✅ רשמתי הוצאה של {amount} ₪")
        else:
            await update.message.reply_text("❌ כתוב: הוצ 200 תחזוקה")

    elif text.startswith("הכנ"):
        parts = text.split()
        amount = next((p for p in parts if p.isdigit()), None)
        if amount:
            note = " ".join(parts[2:]) if len(parts) > 2 else ""
            data["incomes"].append({"amount":int(amount),"note":note,"date":today})
            save_data(data)
            await update.message.reply_text(f"✅ רשמתי הכנסה של {amount} ₪")
        else:
            await update.message.reply_text("❌ כתוב: הכנ 500 מכונה1")

    elif "סיכום" in text:
        mi = sum(i["amount"] for i in data["incomes"] if i["date"].startswith(month))
        me = sum(e["amount"] for e in data["expenses"] if e["date"].startswith(month))
        ti = sum(i["amount"] for i in data["incomes"])
        te = sum(e["amount"] for e in data["expenses"])
        await update.message.reply_text(
            f"📊 סיכום החודש:\n💰 הכנסות: {mi} ₪\n💸 הוצאות: {me} ₪\n📈 רווח החודש: {mi-me} ₪\n\n📊 סה״כ כולל:\n📈 רווח כולל: {ti-te} ₪"
        )
    else:
        await update.message.reply_text("שלח:\n💸 הוצ 200 תחזוקה\n💰 הכנ 500 מכונה1\n📊 סיכום")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("בוט פועל!")
    app.run_polling()

if __name__ == "__main__":
    main()
