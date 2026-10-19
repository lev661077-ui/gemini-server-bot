import os
import json
from http.server import BaseHTTPRequestHandler
import aiohttp
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

async def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    async with aiohttp.ClientSession() as session:
        await session.post(url, json={"chat_id": chat_id, "text": text})

async def ask_gemini(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"contents": [{"parts": [{"text": text}]}]}) as resp:
            data = await resp.json()
            try:
                return data['candidates'][0]['content']['parts'][0]['text']
            except:
                return "Ошибка генерации ответа."

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update = json.loads(post_data)
        
        if "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"]["text"]
            
            # Запускаем асинхронно, чтобы Vercel не выдал таймаут
            asyncio.run(send_message(chat_id, "Думаю..."))
            reply = asyncio.run(ask_gemini(text))
            asyncio.run(send_message(chat_id, reply))
            
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
