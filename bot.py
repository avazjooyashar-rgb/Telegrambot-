import os
import traceback

import telebot
from telebot import types

from config import *
from utils import RateLimiter, safe_remove
from queue_manager import TaskQueue
from downloader import download_instagram, extract_audio, download_music
from recognizer import recognize_audio
from music_links import build_links


os.makedirs(BASE_DIR, exist_ok=True)


bot = telebot.TeleBot(
    TOKEN,
    threaded=True
)


limiter = RateLimiter(
    RATE_LIMIT_SEC
)


def send_safe(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print("SEND ERROR:", e)



def cleanup(files):

    if not files:
        return

    if isinstance(files, str):
        files = [files]

    for f in files:
        try:
            safe_remove(f)
        except:
            pass



def create_keyboard(result):

    links = build_links(result)

    keyboard = types.InlineKeyboardMarkup()


    keyboard.add(
        types.InlineKeyboardButton(
            "🔎 جستجوی آهنگ",
            url=links["google"]
        )
    )


    keyboard.add(
        types.InlineKeyboardButton(
            "▶️ YouTube",
            url=links["youtube"]
        ),
        types.InlineKeyboardButton(
            "🎧 Spotify",
            url=links["spotify"]
        )
    )


    keyboard.add(
        types.InlineKeyboardButton(
            "🍎 Apple Music",
            url=links["apple_music"]
        )
    )


    return keyboard



def process(chat_id, url):

    video = None
    audio = None
    music = None


    send_safe(
        bot.send_message,
        chat_id,
        "⚡ در حال پردازش..."
    )


    try:

        video = download_instagram(
            url,
            BASE_DIR
        )


        if not video:

            return send_safe(
                bot.send_message,
                chat_id,
                "❌ دانلود نشد"
            )


        try:

            with open(video, "rb") as f:

                bot.send_video(
                    chat_id,
                    f
                )

        except Exception as e:

            print(
                "VIDEO SEND:",
                e
            )



        audio = extract_audio(
            video
        )


        if not audio:

            return send_safe(
                bot.send_message,
                chat_id,
                "❌ صدا استخراج نشد"
            )



        result = recognize_audio(
            audio
        )


        if not result:

            return send_safe(
                bot.send_message,
                chat_id,
                "❌ آهنگ پیدا نشد"
            )



        artist = result.get(
            "artist",
            "Unknown"
        )


        title = result.get(
            "title",
            "Unknown"
        )


        keyboard = create_keyboard(
            result
        )


        send_safe(
            bot.send_message,
            chat_id,
            f"🎵 {artist} - {title}",
            reply_markup=keyboard
        )



        music = download_music(
            f"{artist} {title}",
            BASE_DIR
        )


        if music:

            with open(music, "rb") as f:

                bot.send_audio(
                    chat_id,
                    f
                )


    except Exception as e:

        print(
            traceback.format_exc()
        )


        send_safe(
            bot.send_message,
            chat_id,
            f"❌ خطا: {e}"
        )


    finally:

        cleanup(video)
        cleanup(audio)
        cleanup(music)



queue = TaskQueue(
    WORKERS,
    process
)



@bot.message_handler(commands=["start"])
def start(m):

    bot.send_message(
        m.chat.id,
        "🚀 INSTAGRAM MUSIC BOT READY"
    )



@bot.message_handler(func=lambda m: True)
def handler(m):

    if not m.text:
        return


    if not limiter.allow(
        m.from_user.id
    ):

        return bot.send_message(
            m.chat.id,
            "⛔ slow down"
        )



    if "http" not in m.text:

        return bot.send_message(
            m.chat.id,
            "📎 فقط لینک بفرست"
        )



    queue.add(
        (
            m.chat.id,
            m.text
        )
    )



print("BOT RUNNING...")


bot.infinity_polling()
