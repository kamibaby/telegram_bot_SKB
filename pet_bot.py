import os
from aiogram import Bot, Dispatcher, types, executor
from dotenv import load_dotenv
import requests

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

user_history = {}

def search_places(category, location="Москва"):
    url = f"https://search-maps.yandex.ru/v1/"
    params = {
        "apikey": YANDEX_API_KEY,
        "text": category,
        "lang": "ru_RU",
        "ll": "37.618423,55.751244",  # Москва, можно передавать от пользователя
        "type": "biz",
        "results": 5
    }
    response = requests.get(url, params=params)
    results = []
    if response.status_code == 200:
        data = response.json()
        for item in data["features"]:
            name = item["properties"]["CompanyMetaData"]["name"]
            address = item["properties"]["CompanyMetaData"].get("address", "Адрес не указан")
            results.append(f"{name} — {address}")
    else:
        results.append("Произошла ошибка при поиске.")
    return results

@dp.message_handler(commands=["start", "help"])
async def help_command(message: types.Message):
    text = (
        "Привет! Я PET Bot 🐾\n\n"
        "Доступные команды:\n"
        "/grooming – найти груминг-салоны\n"
        "/vets – найти ветеринарные клиники\n"
        "/shops – найти зоомагазины\n"
        "/history – история твоих запросов"
    )
    await message.reply(text)

@dp.message_handler(commands=["grooming", "vets", "shops"])
async def search_command(message: types.Message):
    category = message.text[1:]
    results = search_places(category)
    
    user_id = str(message.from_user.id)
    user_history.setdefault(user_id, []).append(category)
    
    await message.reply("\n".join(results))

@dp.message_handler(commands=["history"])
async def show_history(message: types.Message):
    user_id = str(message.from_user.id)
    history = user_history.get(user_id, [])
    if history:
        await message.reply(f"История запросов: {', '.join(history)}")
    else:
        await message.reply("История пока пуста.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
