import os
import telegram
import schedule
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Налаштування через змінні середовища
TOKEN = os.environ.get("TOKEN", "7991271281:AAEOuPlQeeHak2xUGhusKGENisTaqL60QOg")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@Game_Portal_bot")

# Ініціалізація бота
bot = telegram.Bot(token=TOKEN)

# Список для збереження вже надісланих роздач (щоб уникнути дублювання)
sent_deals = set()

# Логування запуску
print(f"Бот запускається... Час: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Функція для парсингу роздач з Reddit (r/freegames)
def fetch_free_games():
    url = "https://www.reddit.com/r/freegames/new/.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Помилка запиту до Reddit: {response.status_code}")
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
        print(f"Знайдено {len(deals)} нових роздач")
        return deals
    except Exception as e:
        print(f"Помилка при парсингу: {e}")
        return []

# Функція для надсилання повідомлень у канал
def send_deals():
    deals = fetch_free_games()
    if not deals:
        print("Нових роздач немає")
        return

    for deal in deals:
        message = f"🎁 Нова роздача!\n{deal['title']}\nПосилання: {deal['link']}\nЧас: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        try:
            bot.send_message(chat_id=CHANNEL_ID, text=message)
            print(f"Повідомлення надіслано: {deal['title']}")
        except Exception as e:
            print(f"Помилка при відправці: {e}")

# Функція для періодичного виконання
def run_bot():
    # Налаштування першого запуску
    send_deals()
    # Планування перевірок кожні 30 хвилин
    schedule.every(30).minutes.do(send_deals)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_bot()
