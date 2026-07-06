import telebot
import yt_dlp
import os
import requests

TOKEN = "8551612297:AAHnXsshYfx35qTRTxu9IXChmY34HxU2Mfk"
API_KEY =
"2e53b0ad8352f400058497cd4854237e"

bot = telebot.TeleBot(TOKEN)

user_links = {}

# ================= START =================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🎧 ربات حرفه‌ای موزیک آماده است\n\n📩 لینک اینستاگرام را ارسال کنید"
    )

# ================= DOWNLOAD =================
@bot.message_handler(func=lambda m: True)
def handle(message):
    chat_id = message.chat.id
    url = message.text

    user_links[chat_id] = url

    bot.send_message(chat_id, "⏳ در حال دانلود...")

    video_path = f"{chat_id}.mp4"

    try:
        ydl_opts = {
            'outtmpl': video_path,
            'format': 'bv*+ba/b',
            'merge_output_format': 'mp4'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("🎵 پیدا کردن آهنگ", callback_data="find_music")
        markup.add(btn)

        bot.send_video(chat_id, open(video_path, "rb"), reply_markup=markup)

    except Exception as e:
        bot.send_message(chat_id, f"❌ خطا در دانلود: {e}")

# ================= AUDIO ANALYSIS =================
@bot.callback_query_handler(func=lambda call: call.data == "find_music")
def find_music(call):
    chat_id = call.message.chat.id

    video_file = f"{chat_id}.mp4"
    audio_file = f"{chat_id}.mp3"

    bot.send_message(chat_id, "🎧 در حال تحلیل آهنگ...")

    try:
        # استخراج صدا
        os.system(f"ffmpeg -y -i {video_file} -t 10 -vn {audio_file}")

        # ارسال به AudD
        with open(audio_file, "rb") as f:
            res = requests.post(
                "https://api.audd.io/",
                data={"api_token": API_KEY},
                files={"file": f}
            )

        data = res.json()

        if data.get("status") == "success" and data.get("result"):
            artist = data["result"]["artist"]
            title = data["result"]["title"]

            query = f"{artist} {title}"

            bot.send_message(chat_id, f"🎵 پیدا شد:\n{query}\n⏳ در حال دانلود...")

            audio_out = f"{chat_id}_full.mp3"

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': audio_out,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"ytsearch1:{query}"])

            bot.send_audio(chat_id, open(audio_out, "rb"))

            os.remove(audio_out)

        else:
            bot.send_message(chat_id, "❌ آهنگ پیدا نشد")

        os.remove(audio_file)

    except Exception as e:
        bot.send_message(chat_id, f"❌ خطا: {e}")

# ================= RUN =================
bot.polling()
