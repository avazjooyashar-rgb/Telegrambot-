import telebot
import yt_dlp
import os
import glob
import time

TOKEN ="8551612297:AAHnXsshYfx35qTRTxu9IXChmY34HxU2Mfk"
bot = telebot.TeleBot(TOKEN)


def clean_files():
    for f in glob.glob("video.*"):
        try:
            os.remove(f)
        except:
            pass


def download_yt(url):
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'best[ext=mp4]/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'retries': 5,
        'fragment_retries': 5,
        'socket_timeout': 25
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    files = glob.glob("video.*")
    return files[0] if files else None


@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🎥 لینک اینستاگرام رو بفرست")


@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text.strip()

    if "instagram.com" not in url:
        bot.send_message(m.chat.id, "❌ فقط لینک اینستا")
        return

    bot.send_message(m.chat.id, "⏳ در حال دانلود...")

    clean_files()

    file_path = None

    for i in range(3):
        try:
            file_path = download_yt(url)
            if file_path:
                break
        except Exception as e:
            print(f"Try {i+1} failed:", e)
            time.sleep(2)

    if not file_path:
        bot.send_message(m.chat.id, "❌ دانلود نشد (محدود یا private)")
        return

    try:
        with open(file_path, "rb") as f:
            bot.send_video(m.chat.id, f)

        os.remove(file_path)

    except Exception as e:
        print(e)
        bot.send_message(m.chat.id, "❌ خطا در ارسال فایل")


bot.infinity_polling(timeout=60, long_polling_timeout=60)
