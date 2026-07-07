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

        "format": "bv*+ba/best",

        "merge_output_format": "mp4",

        "noplaylist": True,

        "quiet": True,

        "no_warnings": True,

        "retries": 10,

        "fragment_retries": 10,

        "socket_timeout": 60
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
            f"INSTAGRAM DOWNLOAD ERROR: {e}"
        )


    return None





def get_duration(path):

    try:

        result = subprocess.run(

            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                path
            ],

            capture_output=True,
            text=True
        )


        return float(
            result.stdout.strip()
        )


    except:

        return 60





def extract_audio(video_path):

    base = video_path.rsplit(
        ".",
        1
    )[0]


    audio_file = (
        base +
        "_clip.wav"
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

                "-c:a",
                "pcm_s16le",

                audio_file
            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL
        )


        if os.path.exists(audio_file):

            return [
                audio_file
            ]


    except Exception as e:

        logging.error(
            f"AUDIO ERROR: {e}"
        )


    return None





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
            f"MUSIC DOWNLOAD ERROR: {e}"
        )


    return None
