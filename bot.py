import telebot
import yt_dlp
import os
import requests

TOKEN = "8551612297:AAHnXsshYfx35qTRTxu9IXChmY34HxU2Mfk"
bot = telebot.TeleBot(TOKEN)

user_links = {}

# ================= START =================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🎧 به واتس موزیک خوش آمدید\n\n"
        "📩 لینک ریلز یا پست اینستاگرام را ارسال کنید"
    )

# ================= دریافت لینک =================
@bot.message_handler(func=lambda m: True)
def handle(message):
    url = message.text
    chat_id = message.chat.id

    user_links[chat_id] = url

    bot.send_message(chat_id, "⏳ در حال دانلود ویدیو...")

    video_path = f"{chat_id}.mp4"

    try:
        ydl_opts = {
            'outtmpl': video_path,
            'format': 'bv*+ba/b',
            'merge_output_format': 'mp4'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # ارسال ویدیو
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(
            "🎵 پیدا کردن آهنگ",
            callback_data="find_music"
        )
        markup.add(btn)

        bot.send_video(chat_id, open(video_path, "rb"), reply_markup=markup)

    except Exception as e:
        bot.send_message(chat_id, f"❌ خطا در دانلود: {e}")

# ================= پیدا کردن آهنگ =================
@bot.callback_query_handler(func=lambda call: call.data == "find_music")
def find_music(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)

    if not url:
        bot.send_message(chat_id, "❌ لینک پیدا نشد دوباره ارسال کن")
        return

    bot.send_message(chat_id, "🎧 در حال تحلیل صدا...")

    video_file = f"{chat_id}.mp4"
    audio_clip = f"{chat_id}_clip.mp3"

    try:
        # 🔥 فقط 2 ثانیه صدا (از ثانیه 1)
        os.system(f"ffmpeg -y -ss 00:00:01 -t 2 -i {video_file} {audio_clip}")

        # =======================
        # 🎧 شبیه‌سازی تشخیص آهنگ
        # (اینجا باید API واقعی مثل ACRCloud بزنی)
        # =======================

        # برای دمو (اسم فرضی)
        song_name = "test song"
        artist = "unknown artist"

        query = f"{song_name} {artist}"

        bot.send_message(chat_id, f"🔍 آهنگ پیدا شد:\n{query}\n⏳ در حال دانلود نسخه کامل...")

        # دانلود آهنگ کامل از یوتیوب
        audio_file = f"{chat_id}_full.mp3"

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_file,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:{query}"])

        bot.send_audio(chat_id, open(audio_file, "rb"))

        # پاکسازی
        os.remove(audio_clip)
        os.remove(audio_file)

    except Exception as e:
        bot.send_message(chat_id, f"❌ خطا: {e}")

# ================= RUN =================
bot.polling()
