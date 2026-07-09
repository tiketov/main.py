import json
import os
import telebot
from telebot import types

TOKEN = ""
ADMIN_ID = 6764036318
DB_FILE = "iq.json"

bot = telebot.TeleBot(TOKEN)

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def find_answer(question, db):
    question_lower = question.lower().strip()
    
    if question_lower in db:
        return db[question_lower]
    
    for key, value in db.items():
        if question_lower in key.lower() or key.lower() in question_lower:
            return value
    
    return None
    
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "салем или салам я котакграм задавай мне вопрос"
    )

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "ты не админ кетче нахуй")
        return
    
    db = load_db()
    if not db:
        bot.reply_to(message, "база пуста")
        return
    
    text = "**база ответов:**\n\n"
    for i, (q, a) in enumerate(db.items(), 1):
        text += f"добавлено"
        if len(text) > 3500:
            text += "... (слишком много записей)"
            break
    
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['add'])
def add_record(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "ты не админ кетче нахуй")
        return
    
    try:
        text = message.text.replace('/add', '').strip()
        if '|' not in text:
            bot.reply_to(message, "формат: /add вопрос | ответ")
            return
        
        question, answer = text.split('|', 1)
        question = question.strip().lower()
        answer = answer.strip()
        
        if not question or not answer:
            bot.reply_to(message, "вопрос и ответ не могут быть пустыми")
            return
        
        db = load_db()
        db[question] = answer
        save_db(db)
        
        bot.reply_to(
            message,
            f"добавлено"
        )
    
    except Exception as e:
        bot.reply_to(message, f"ошибка: {e}")

@bot.message_handler(commands=['del'])
def delete_record(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "ты не админ кетче нахуй")
        return
    
    question = message.text.replace('/del', '').strip().lower()
    
    if not question:
        bot.reply_to(message, "формат: /del вопрос")
        return
    
    db = load_db()
    
    if question in db:
        del db[question]
        save_db(db)
        bot.reply_to(message, f"удалено")
    else:
        bot.reply_to(message, "такого вопроса нету")

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "ты не админ кетче нахуй")
        return
    
    db = load_db()
    bot.reply_to(message, f"админ панель")

@bot.message_handler(func=lambda message: True)
def handle_message(message): 
    user_question = message.text
    db = load_db()
    
    answer = find_answer(user_question, db)
    
    if answer:
        bot.reply_to(message, f"{answer}")
    else:
        bot.reply_to(
            message,
            "я что ебу чтоли что ты мне несешь говори нормально"
        )

if __name__ == "__main__":
    bot.infinity_polling()