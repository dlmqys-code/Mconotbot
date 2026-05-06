import os, json
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
DATA_FILE = "vending_data.json"

def load():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"expenses":[],"incomes":[]}

def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 שלום!\nהוצ 200 תחזוקה\nהכנ 500\nסיכום")

async def msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    t = update.message.text
    data = load()
    today = datetime.now().strftime("%Y-%m-%d")
    month = today[:7]
    if t.startswith("הוצ"):
        nums = [x for x in t.split() if x.isdigit()]
        if nums:
            data["expenses"].append({"amount":int(nums[0]),"note":t,"date":today})
            save(data)
            await update.message.reply_text(f"✅ הוצאה {nums[0]} ₪")
    elif t.startswith("הכנ"):
        nums = [x for x in t.split() if x.isdigit()]
        if nums:
            data["incomes"].append({"amount":int(nums[0]),"note":t,"date":today})
            save(data)
            await update.message.reply_text(f"✅ הכנסה {nums[0]} ₪")
    elif "סיכום" in t:
        mi = sum(i["amount"] for i in data["incomes"] if i["date"][:7]==month)
        me = sum(e["amount"] for e in data["expenses"] if e["date"][:7]==month)
        await update.message.reply_text(f"📊 החודש:\n💰 {mi} ₪\n💸 {me} ₪\n📈 {mi-me} ₪")
    else:
        await update.message.reply_text("הוצ 200\nהכנ 500\nסיכום")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
