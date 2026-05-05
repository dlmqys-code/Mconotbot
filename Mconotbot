import os
import json
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import anthropic

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
ANTHROPIC_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
DATA_FILE      = "vending_data.json"

logging.basicConfig(level=logging.INFO)
client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"machines":[{"id":1,"name":"מכונה #1","location":"","status":"תקינה"}],"expenses":[],"incomes":[],"reminders":[]}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_summary(data):
    total_income   = sum(float(i["amount"]) for i in data["incomes"])
    total_expenses = sum(float(e["amount"]) for e in data["expenses"])
    profit = total_income - total_expenses
    month = datetime.now().strftime("%Y-%m")
    month_income   = sum(float(i["amount"]) for i in data["incomes"]  if i.get("date","").startswith(month))
    month_expenses = sum(float(e["amount"]) for e in data["expenses"] if e.get("date","").startswith(month))
    return {"total_income":total_income,"total_expenses":total_expenses,"profit":profit,"month_income":month_income,"month_expenses":month_expenses,"machines_count":len(data["machines"]),"pending_reminders":len([r for r in data["reminders"] if not r.get("done")])}

SYSTEM_PROMPT = """אתה עוזר חכם לניהול עסק מכונות אוטומטיות בעברית.
תפקידך לזהות את הכוונה ולהגיב קצר וברור.
אם יש פעולה, הוסף בסוף: ACTION:{"type":"...","data":{...}}

סוגי פעולות:
ADD_EXPENSE: {"type":"ADD_EXPENSE","data":{"amount":200,"category":"תחזוקה","note":"..."}}
ADD_INCOME: {"type":"ADD_INCOME","data":{"amount":500,"machine":"מכונה #1","note":"..."}}
UPDATE_MACHINE: {"type":"UPDATE_MACHINE","data":{"name":"מכונה #1","status":"תקלה"}}
ADD_REMINDER: {"type":"ADD_REMINDER","data":{"text":"...","date":"2026-05-10"}}
GET_SUMMARY: {"type":"GET_SUMMARY"}

דוגמאות:
משתמש: שילמתי 300 על תחזוקה
תשובה: ✅ רשמתי הוצאה של 300 ₪
ACTION:{"type":"ADD_EXPENSE","data":{"amount":300,"category":"תחזוקה","note":"תחזוקה"}}

משתמש: ריקנתי מכונה 1 היה 450 שקל
תשובה: 💰 רשמתי הכנסה של 450 ₪
ACTION:{"type":"ADD_INCOME","data":{"amount":450,"machine":"מכונה #1","note":"ריקון"}}

משתמש: מה המצב
תשובה: כאן הסיכום
ACTION:{"type":"GET_SUMMARY"}"""

def parse_action(text):
    if "ACTION:" not in text:
        return None, text
    parts = text.split("ACTION:", 1)
    try:
        return json.loads(parts[1].strip()), parts[0].strip()
    except:
        return None, text

def execute_action(action, data):
    t = action.get("type")
    d = action.get("data", {})
    today = datetime.now().strftime("%Y-%m-%d")
    if t == "ADD_EXPENSE":
        data["expenses"].append({"id":int(datetime.now().timestamp()),"amount":d.get("amount",0),"category":d.get("category","אחר"),"note":d.get("note",""),"date":today})
        save_data(data)
    elif t == "ADD_INCOME":
        data["incomes"].append({"id":int(datetime.now().timestamp()),"amount":d.get("amount",0),"machine":d.get("machine",""),"note":d.get("note",""),"date":today})
        save_data(data)
    elif t == "UPDATE_MACHINE":
        for m in data["machines"]:
            if d.get("name","").replace(" ","") in m["name"].replace(" ",""):
                m["status"] = d.get("status", m["status"])
        save_data(data)
    elif t == "ADD_REMINDER":
        data["reminders"].append({"id":int(datetime.now().timestamp()),"text":d.get("text",""),"date":d.get("date",""),"done":False})
        save_data(data)
    elif t == "GET_SUMMARY":
        s = get_summary(data)
        return f"📊 *סיכום העסק*\n\n💰 הכנסה החודש: {s['month_income']:,.0f} ₪\n💸 הוצאות החודש: {s['month_expenses']:,.0f} ₪\n📈 רווח כולל: {s['profit']:,.0f} ₪\n⚙️ מכונות: {s['machines_count']}\n🔔 תזכורות פתוחות: {s['pending_reminders']}"
    return None

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 שלום! אני בוט VendingOS.\n\nשלח לי:\n• שילמתי 200 על תחזוקה\n• ריקנתי מכונה 1 היה 450 שקל\n• מכונה 2 תקולה\n• מה המצב?", parse_mode="Markdown")

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    data = load_data()
    s = get_summary(data)
    context_info = f"\nנתוני העסק: הכנסה החודש {s['month_income']} ₪, הוצאות {s['month_expenses']} ₪, רווח כולל {s['profit']} ₪, מכונות: {json.dumps(data['machines'], ensure_ascii=False)}"
    response = client.messages.create(model="claude-sonnet-4-20250514",max_tokens=500,system=SYSTEM_PROMPT+context_info,messages=[{"role":"user","content":user_text}])
    full_reply = response.content[0].text
    action, reply_text = parse_action(full_reply)
    extra = execute_action(action, data) if action else None
    await update.message.reply_text(reply_text or "✅", parse_mode="Markdown")
    if extra:
        await update.message.reply_text(extra, parse_mode="Markdown")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 הבוט פועל!")
    app.run_polling()

if __name__ == "__main__":
    main()
