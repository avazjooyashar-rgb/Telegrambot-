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


os.makedirs(
    BASE_DIR,
    exist_ok=True
)


bot = telebot.TeleBot(
    TOKEN,
    threaded=True
)


limiter = RateLimiter(
    RATE_LIMIT_SEC
)



def send_safe(func, *args, **kwargs):

    try:
        return func(
            *args,
            **kwargs
        )

    except Exception as e:

        print(
            "SEND ERROR:",
            e
        )



def cleanup(files):

    if not files:
        return

    if isinstance(
        files,
        str
    ):

        files = [files]


    for f in files:

        try:
            safe_remove(f)

        except:
            pass





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
                "❌ دانلود ویدیو ناموفق بود"
            )



        try:

            with open(
                video,
                "rb"
            ) as f:

                bot.send_video(
                    chat_id,
                    f
                )

        except Exception:

            pass




        audio = extract_audio(
            video
        )


        if not audio:

            return send_safe(
                bot.send_message,
                chat_id,
                "❌ استخراج صدا انجام نشد"
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



        links = build_links(
            result
        )



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

            try:

                with open(
                    music,
                    "rb"
                ) as f:

                    bot.send_audio(
                        chat_id,
                        f
                    )


            except Exception as e:

                print(
                    "AUDIO SEND ERROR:",
                    e
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





@bot.message_handler(
    commands=["start"]
)
def start(message):

    bot.send_message(
        message.chat.id,
        "🚀 INSTAGRAM MUSIC BOT READY"
    )





@bot.message_handler(
    func=lambda m: True
)
def handler(message):


    if not message.text:

        return



    if not limiter.allow(
        message.from_user.id
    ):

        return bot.send_message(
            message.chat.id,
            "⛔ slow down"
        )



    if "http" not in message.text:

        return bot.send_message(
            message.chat.id,
            "📎 فقط لینک اینستا بفرست"
        )



    queue.add(
        (
            message.chat.id,
            message.text
        )
    )





print(
    "BOT RUNNING..."
)


bot.infinity_polling()
