import os
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from google import genai

# Берем токены из переменных окружения (которые ты потом вставишь в Render)
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Инициализация бота
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Инициализация Gemini (используем модель 2.0 Flash — она умная и быстрая)
client = genai.Client(api_key=GEMINI_KEY)
MODEL_ID = "gemini-2.0-flash" 

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я AI-бот на базе Gemini. Напиши мне любой вопрос, и я отвечу! 🧠")

@dp.message(F.text)
async def handle_message(message: types.Message):
    # Показываем, что бот "печатает"
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        # Отправляем запрос в Gemini
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=message.text
        )
        # Отправляем ответ (Telegram не принимает сообщения длиннее 4096 символов)
        await message.answer(response.text[:4000])
    except Exception as e:
        # Если что-то пошло не так (например, закончился лимит), бот напишет ошибку
        await message.answer(f"❌ Ошибка: {e}")

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
