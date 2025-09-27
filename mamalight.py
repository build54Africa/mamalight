import os
import sqlite3
import time
import re
from datetime import datetime, timedelta
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import cohere

# Load environment variables from .env
load_dotenv()

# Initialize Flask app and scheduler
app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

# Initialize Twilio client
client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

# Initialize Cohere client
co = cohere.ClientV2(os.getenv("COHERE_API_KEY"))

# Database setup
DB_FILE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE,
            name TEXT,
            gestational_age INTEGER,
            next_checkup TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def add_user(phone, name, gest_age, next_checkup):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO users (phone, name, gestational_age, next_checkup)
        VALUES (?, ?, ?, ?)
    ''', (phone, name, gest_age, next_checkup))
    conn.commit()
    conn.close()

def get_user(phone):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE phone=?', (phone,))
    user = c.fetchone()
    conn.close()
    return user

def update_next_checkup(phone, next_date):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE users SET next_checkup=? WHERE phone=?', (next_date, phone))
    conn.commit()
    conn.close()

# Cohere Chat API with friendly formatting
def cohere_chat(message):
    try:
        response = co.chat(
            model="command-r-plus-08-2024",
            messages=[{"role": 'user', "content": message}],
            max_tokens=400
        )
        text = response.message.content[0].text

        # # # # Remove markdown symbols
        clean_text = re.sub(r"[*_`#>-]", "", text).strip()

         # Add friendly emojis and prefix for WhatsApp
        friendly_text = f"🌸 MamaLight says:\n{clean_text}"

        # # # # Add line breaks for readability after periods
        friendly_text = re.sub(r"(\. )", r".\n", friendly_text)

  

        return friendly_text

    except Exception as e:
        return f"Error contacting Cohere API: {e}"

# Reminder system
def send_personalized_reminder(phone, name):
    message_prompt = f"Send a warm, encouraging antenatal checkup reminder to {name} with simple health tips, keeping it short and concise"
    message = cohere_chat(message_prompt)

    client.messages.create(
        from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
        body=message,
        to=f'whatsapp:{phone}'
    )

    # Schedule next checkup reminder after 4 weeks
    next_date = datetime.now() + timedelta(weeks=4)
    update_next_checkup(phone, next_date.strftime("%Y-%m-%d %H:%M:%S"))
    scheduler.add_job(send_personalized_reminder, 'date', run_date=next_date, args=[phone, name])

def schedule_first_reminder(phone, name, first_date):
    scheduler.add_job(send_personalized_reminder, 'date', run_date=first_date, args=[phone, name])

# Flask route for WhatsApp messages
@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.values.get('Body', '').strip()
    phone = request.values.get('From', '').replace('whatsapp:', '')
    resp = MessagingResponse()
    msg = resp.message()
    user = get_user(phone)

    if incoming_msg.lower().startswith("register"):
        try:
            parts = incoming_msg.split(" ", 1)[1].split(",")
            name = parts[0].strip()
            gest_age = int(parts[1].strip())
            first_checkup = datetime.now() + timedelta(weeks=4)
            add_user(phone, name, gest_age, first_checkup.strftime("%Y-%m-%d %H:%M:%S"))
            schedule_first_reminder(phone, name, first_checkup)
            msg.body(f"🌸 Registration complete! 🌸\nYour first checkup reminder will be sent on {first_checkup.strftime('%Y-%m-%d %H:%M:%S')}\nWelcome to MamaLight, {name}!")
        except Exception:
            msg.body("Registration failed. Use format:\nregister Name, gestational_age")
    elif incoming_msg.lower() in ["nutrition", "tips"]:
        msg.body("🌸 MamaLight Tip:\nEat a balanced diet with fruits, vegetables, proteins, and iron-rich foods.\nStay hydrated and take prenatal vitamins daily.")
    elif incoming_msg.lower() == "next checkup":
        if user:
            msg.body(f"🌸 MamaLight Reminder:\nYour next antenatal checkup is on {user[4]}")
        else:
            msg.body("You are not registered yet. Send:\nregister Name, gestational_age")
    else:
        answer = cohere_chat(incoming_msg)
        msg.body(answer)

    return str(resp)

if __name__ == "__main__":
    app.run(port=5000)