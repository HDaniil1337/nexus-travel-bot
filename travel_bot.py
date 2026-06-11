import os
import requests
import random
from datetime import datetime

# ============================================================
#  НАСТРОЙКИ
# ============================================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "ВАШ_ТОКЕН_ЗДЕСЬ")
CHANNEL_ID     = os.getenv("CHANNEL_ID", "-1003770552952")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAQ.Ab8RN6IFe721bYvnqYqRFBwd8NTBBtg8WiwE8prW1npGEd0AMQ")
# ============================================================

CITIES = [
    "Лиссабон", "Барселона", "Прага", "Будапешт", "Краков",
    "Амстердам", "Вена", "Рим", "Афины", "Дубровник",
    "Таллин", "Рига", "Варшава", "Загреб", "Любляна",
    "Брюссель", "Копенгаген", "Стокгольм", "Осло", "Хельсинки",
    "Порту", "Севилья", "Валенсия", "Флоренция", "Неаполь",
    "Мальта", "Никосия", "Тбилиси", "Стамбул", "Белград",
]

TOPICS = [
    ("скрытые места",             "🗺️"),
    ("бюджетный маршрут",         "💶"),
    ("еда и рестораны",           "🍜"),
    ("лайфхаки путешественника",  "💡"),
    ("уикенд поездка",            "✈️"),
    ("культура и история",        "🏛️"),
    ("лучшие кафе",               "☕"),
    ("транспорт и логистика",     "🚆"),
]

SCHEDULE = {
    "08": ("скрытые места",            "🗺️"),
    "12": ("бюджетный маршрут",        "💶"),
    "17": ("еда и рестораны",          "🍜"),
    "21": ("лайфхаки путешественника", "💡"),
}


def get_topic_for_now():
    hour = datetime.now().strftime("%H")
    if hour in SCHEDULE:
        return SCHEDULE[hour]
    return random.choice(TOPICS)


def generate_post(city, topic, emoji):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    )

    prompt = f"""Ты — редактор Telegram-канала о путешествиях "ATLAS Travel".

Стиль: дружелюбный и живой, короткие абзацы, эмодзи уместно.
Язык: русский, иногда английские слова органично.

Напиши один пост о городе {city} на тему: {emoji} {topic}.

Требования:
- 150-220 слов
- Начни с яркого заголовка с эмодзи
- Конкретные советы или интересные факты
- Заверши вовлекающим вопросом или призывом к действию
- В конце добавь: #ATLASTravel #{city.replace(' ', '')}

Только текст поста, без пояснений."""

    body = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, json=body, timeout=20)
    data = response.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        print(f"❌ Ошибка Gemini: {data}")
        return None


def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    response = requests.post(url, json=payload, timeout=15)
    result = response.json()

    if result.get("ok"):
        print(f"✅ Опубликовано! Message ID: {result['result']['message_id']}")
        return True
    else:
        print(f"❌ Ошибка Telegram: {result.get('description')}")
        return False


def main():
    city  = random.choice(CITIES)
    topic, emoji = get_topic_for_now()

    print(f"🌍 Город: {city}")
    print(f"📌 Тема:  {emoji} {topic}")
    print("⏳ Генерирую пост через Gemini...")

    post_text = generate_post(city, topic, emoji)
    if not post_text:
        return

    print("\n--- ТЕКСТ ПОСТА ---")
    print(post_text)
    print("-------------------\n")

    send_to_telegram(post_text)


if __name__ == "__main__":
    main()
