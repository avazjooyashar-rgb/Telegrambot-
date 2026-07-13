import os
import uuid
import subprocess
import logging

import yt_dlp


logging.basicConfig(
    filename="downloader.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)



def download_instagram(url, base_dir):

    os.makedirs(
        base_dir,
        exist_ok=True
    )

    uid = str(uuid.uuid4())

    output = os.path.join(
        base_dir,
        f"{uid}.%(ext)s"
    )


    options = {

        "outtmpl": output,

        "format": "bestvideo*+bestaudio/best",

        "merge_output_format": "mp4",

        "noplaylist": True,

        "quiet": True,

        "no_warnings": True,

        "retries": 10,

        "fragment_retries": 10,

        "socket_timeout": 60,

        "ignoreerrors": True

    }


    try:

        with yt_dlp.YoutubeDL(options) as ydl:

            ydl.download(
                [url]
            )


        for file in os.listdir(base_dir):

            if file.startswith(uid):

                return os.path.join(
                    base_dir,
                    file
                )


    except Exception as e:

        logging.error(
            f"INSTAGRAM ERROR: {e}"
        )


    return None





def extract_audio(video_path):

    base = video_path.rsplit(
        ".",
        1
    )[0]


    audio_file = (
        base +
        "_audio.wav"
    )


    try:

        subprocess.run(

            [
                "ffmpeg",
                "-y",

                "-i",
                video_path,

                "-vn",

                "-ac",
                "1",

                "-ar",
                "44100",

                "-sample_fmt",
                "s16",

                audio_file
            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL,

            timeout=60

        )


        if os.path.exists(audio_file):

            return [
                audio_file
            ]


    except Exception as e:

        logging.error(
            f"EXTRACT ERROR: {e}"
        )


    return None





def create_chunks(audio_path):

    chunks = []

    base = audio_path.rsplit(
        ".",
        1
    )[0]


    times = [
        0,
        10,
        20
    ]


    for index, start in enumerate(times):

        output = (
            f"{base}_chunk_{index}.wav"
        )


        try:

            subprocess.run(

                [
                    "ffmpeg",
                    "-y",

                    "-ss",
                    str(start),

                    "-i",
                    audio_path,

                    "-t",
                    "15",

                    "-ac",
                    "1",

                    "-ar",
                    "44100",

                    output
                ],

                stdout=subprocess.DEVNULL,

                stderr=subprocess.DEVNULL

            )


            if os.path.exists(output):

                chunks.append(
                    output
                )


        except Exception:
            pass


    return chunks





def download_music(query, base_dir):

    os.makedirs(
        base_dir,
        exist_ok=True
    )


    uid = str(uuid.uuid4())


    output = os.path.join(
        base_dir,
        f"{uid}.%(ext)s"
    )


    options = {

        "outtmpl": output,

        "format": "bestaudio/best",

        "noplaylist": True,

        "quiet": True,

        "no_warnings": True,

        "default_search": "ytsearch1",

        "postprocessors": [

            {

                "key": "FFmpegExtractAudio",

                "preferredcodec": "mp3",

                "preferredquality": "192"

            }

        ]

    }


    try:

        with yt_dlp.YoutubeDL(options) as ydl:

            ydl.download(
                [
                    f"ytsearch1:{query}"
                ]
            )


        for file in os.listdir(base_dir):

            if file.startswith(uid):

                return os.path.join(
                    base_dir,
                    file
                )


    except Exception as e:

        logging.error(
            f"MUSIC ERROR: {e}"
        )


    return None
