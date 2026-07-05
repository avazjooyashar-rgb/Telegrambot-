import telebot
import yt_dlp
import os

TOKEN = "8551612297:AAHnXsshYfx35qTRTxu9IXChmY34HxU2Mfk"
bot = telebot.TeleBot(TOKEN)

user_links = {}

# ================= START =================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🎧 به واتس موزیک خوش آمدید\n\n📩 لینک ریلز یا پست اینستاگرام را ارسال کنید"
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
            'outtmpl': f'{chat_id}.%(ext)s',
            'format': 'bv*+ba/b',
            'merge_output_format': 'mp4'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

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
        # استخراج 2 ثانیه صدا
        os.system(f"ffmpeg -y -ss 00:00:01 -t 2 -i {video_file} {audio_clip}")

        # شبیه‌سازی تشخیص آهنگ
        song_name = "test song"
        artist = "unknown artist"
        query = f"{song_name} {artist}"

        bot.send_message(chat_id, f"🔍 آهنگ پیدا شد:\n{query}\n⏳ در حال دانلود...")

        # دانلود آهنگ کامل
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{chat_id}_full.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:{query}"])

        final_audio = f"{chat_id}_full.mp3"
        bot.send_audio(chat_id, open(final_audio, "rb"))

        # پاکسازی
        os.remove(audio_clip)
        os.remove(final_audio)

    except Exception as e:
        bot.send_message(chat_id, f"❌ خطا: {e}")

# ================= RUN =================
bot.polling()
