import telebot
import yt_dlp
import os
import subprocess

TOKEN = "8551612297:AAHnXsshYfx35qTRTxu9IXChmY34HxU2Mfk"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "📩 لینک بفرست")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text
    cid = m.chat.id

    video = f"{cid}.mp4"
    audio = f"{cid}.mp3"

    try:
        # دانلود ویدیو
        ydl_opts = {
            'outtmpl': f'{cid}.%(ext)s',
            'format': 'mp4'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # پیدا کردن فایل واقعی (خیلی مهم)
        for f in os.listdir():
            if f.startswith(str(cid)) and f.endswith(".mp4"):
                video = f

        bot.send_video(cid, open(video, "rb"))

        # تبدیل به mp3
        subprocess.run([
            "ffmpeg", "-y",
            "-i", video,
            audio
        ])

        bot.send_audio(cid, open(audio, "rb"))

        os.remove(video)
        os.remove(audio)

    except Exception as e:
        bot.send_message(cid, f"❌ خطا: {e}")

bot.polling()
