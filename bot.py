import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters

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

def start(update, ctx):
    update.message.reply_text("👋 שלום!\nהוצ 200 תחזוקה\nהכנ 500\nסיכום")

def msg(update, ctx):
    t = update.message.text
    data = load()
    today = datetime.now().strftime("%Y-%m-%d")
    month = today[:7]
    if t.startswith("הוצ"):
        nums = [x for x in t.split() if x.isdigit()]
        if nums:
            data["expenses"].append({"amount":int(nums[0]),"note":t,"date":today})
            save(data)
            update.message.reply_text(f"✅ הוצאה {nums[0]} ₪")
    elif t.startswith("הכנ"):
        nums = [x for x in t.split() if x.isdigit()]
        if nums:
            data["incomes"].append({"amount":int(nums[0]),"note":t,"date":today})
            save(data)
            update.message.reply_text(f"✅ הכנסה {nums[0]} ₪")
    elif "סיכום" in t:
        mi = sum(i["amount"] for i in data["incomes"] if i["date"][:7]==month)
        me = sum(e["amount"] for e in data["expenses"] if e["date"][:7]==month)
        update.message.reply_text(f"📊 החודש:\n💰 {mi} ₪\n💸 {me} ₪\n📈 {mi-me} ₪")
    else:
        update.message.reply_text("הוצ 200\nהכנ 500\nסיכום")

if __name__ == "__main__":
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, msg))
    updater.start_polling()
    updater.idle()
