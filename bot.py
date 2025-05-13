import os
import telegram
from telegram.ext import Application, CommandHandler
import schedule
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Налаштування токена бота та ID каналу
TOKEN = "7991271281:AAEOuPlQeeHak2xUGhusKGENisTaqL60QOg"  # Замініть на ваш токен від @BotFather
CHANNEL_ID = "@Game_Portal_bot"  # Замініть на ID вашого каналу (наприклад, @YourChannel)

# Ініціалізація бота
bot = telegram.Bot(token=TOKEN)
app = Application.builder().token(TOKEN).build()

# Список для збереження вже надісланих роздач (щоб уникнути дублювання)
sent_deals = set()

# Функція для парсингу роздач з Reddit (r/freegames)
def fetch_free_games():
    url = "https://www.reddit.com/r/freegames/new/.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    data = response.json()
    posts = data["data"]["children"]
    deals = []

    for post in posts[:5]:  # Беремо 5 найновіших постів
        title = post["data"]["title"]
        link = post["data"]["url"]
        if "self.freegames" not in link:  # Фільтруємо пости, які не є прямими посиланнями на роздачі
            if title not in sent_deals:
                deals.append({"title": title, "link": link})
                sent_deals.add(title)
    return deals

# Функція для надсилання повідомлень у канал
async def send_deals():
    deals = fetch_free_games()
    if not deals:
        return

    for deal in deals:
        message = f"🎁 Нова роздача!\n{deal['title']}\nПосилання: {deal['link']}\nЧас: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        await bot.send_message(chat_id=CHANNEL_ID, text=message)

# Функція для команди /start
async def start(update, context):
    await update.message.reply_text("Бот запущено! Я надсилатиму знижки та роздачі у канал.")

# Функція для періодичного виконання
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(60)

# Головна функція
def main():
    # Додаємо обробник команди /start
    app.add_handler(CommandHandler("start", start))

    # Налаштування періодичних перевірок (кожні 30 хвилин)
    schedule.every(30).minutes.do(lambda: app.run_async(send_deals))

    # Запускаємо бота
    app.run_polling()

    # Запускаємо графік у окремому потоці
    import threading
    threading.Thread(target=run_schedule, daemon=True).start()

if __name__ == "__main__":
    main()
