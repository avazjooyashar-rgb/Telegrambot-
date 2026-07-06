import os
import telebot

from config import *
from utils import RateLimiter, safe_remove
from queue_manager import TaskQueue
from downloader import download_instagram, extract_audio, download_music
from recognizer import recognize_audio

os.makedirs(BASE_DIR, exist_ok=True)

bot = telebot.TeleBot(TOKEN, threaded=True)
limiter = RateLimiter(RATE_LIMIT_SEC)


def send_safe(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except:
        pass


def process(chat_id, url):
    send_safe(bot.send_message, chat_id, "⚡ در حال پردازش...")

    try:
        video = download_instagram(url, BASE_DIR)
    except Exception as e:
        return send_safe(bot.send_message, chat_id, f"❌ دانلود خطا: {e}")

    try:
        with open(video, "rb") as f:
            bot.send_video(chat_id, f)
    except:
        pass

    audio = extract_audio(video)

    result = recognize_audio(audio)

    if not result:
        return send_safe(bot.send_message, chat_id, "❌ آهنگ پیدا نشد")

    artist, title = result
    send_safe(bot.send_message, chat_id, f"🎵 {artist} - {title}")

    music = download_music(f"{artist} {title}", BASE_DIR)

    try:
        with open(music, "rb") as f:
            bot.send_audio(chat_id, f)
    except:
        pass

    safe_remove(video)
    safe_remove(audio)
    safe_remove(music)


queue = TaskQueue(WORKERS, process)


@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id, "🚀 INSTAGRAM MUSIC BOT READY")


@bot.message_handler(func=lambda m: True)
def handler(m):
    if not m.text:
        return

    if not limiter.allow(m.from_user.id):
        return bot.send_message(m.chat.id, "⛔ slow down")

    if "http" not in m.text:
        return bot.send_message(m.chat.id, "📎 فقط لینک اینستا بفرست")

    queue.add((m.chat.id, m.text))


print("BOT RUNNING...")
bot.infinity_polling(skip_pending=True)
