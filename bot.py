import telebot
import yt_dlp
import os
import requests
import uuid
import subprocess

TOKEN = "8551612297:AAHnXsshYfx35qTRTxu9IXChmY34HxU2Mfk"
API_KEY = "2e53b0ad8352f400058497cd4854237e"

bot = telebot.TeleBot(TOKEN)

# ================= START =================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🎧 ربات آماده است\n📩 لینک اینستاگرام را ارسال کنید"
    )

# ================= MAIN HANDLER =================
@bot.message_handler(func=lambda m: True)
def handle(message):
    chat_id = message.chat.id
    url = message.text.strip()

    bot.send_message(chat_id, "⏳ در حال دانلود ویدیو...")

    uid = str(uuid.uuid4())
    video_path = f"/tmp/{chat_id}_{uid}.mp4"
    audio_path = f"/tmp/{chat_id}_{uid}.mp3"

    try:
        # ===== Download Instagram Video =====
        ydl_opts = {
            'outtmpl': video_path,
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'cachedir': False
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(video_path):
            bot.send_message(chat_id, "❌ دانلود ناموفق بود")
            return

        # send video
        bot.send_video(chat_id, open(video_path, "rb"))

        bot.send_message(chat_id, "🎧 در حال تشخیص آهنگ...")

        # ===== extract short audio for recognition =====
        subprocess.run(
            ["ffmpeg", "-y", "-i", video_path, "-vn", "-t", "10", audio_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # ===== AudD recognition =====
        with open(audio_path, "rb") as f:
            res = requests.post(
                "https://api.audd.io/",
                data={"api_token": API_KEY},
                files={"file": f}
            )

        data = res.json()

        if not data.get("result"):
            bot.send_message(chat_id, "❌ آهنگ پیدا نشد")
            cleanup(video_path, audio_path)
            return

        artist = data["result"]["artist"]
        title = data["result"]["title"]

        query = f"{artist} - {title} official audio"

        bot.send_message(chat_id, f"🎵 پیدا شد:\n{query}\n🎧 در حال دانلود آهنگ کامل...")

        # ===== download full song =====
        audio_out = f"/tmp/{chat_id}_{uid}_full.mp3"

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_out,
            'noplaylist': True,
            'cachedir': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:{query}"])

        if os.path.exists(audio_out):
            bot.send_audio(chat_id, open(audio_out, "rb"))
        else:
            bot.send_message(chat_id, "❌ دانلود آهنگ کامل ناموفق بود")

        cleanup(video_path, audio_path, audio_out)

    except Exception as e:
        bot.send_message(chat_id, f"❌ خطا: {e}")

# ================= CLEANUP =================
def cleanup(*files):
    for f in files:
        try:
            if f and os.path.exists(f):
                os.remove(f)
        except:
            pass

# ================= RUN =================
bot.polling(none_stop=True, timeout=60)
