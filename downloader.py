import os
import uuid
import subprocess
import yt_dlp
import logging
import math


logging.basicConfig(
    filename="downloader.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# =========================
# VIDEO DOWNLOAD
# =========================

def download_instagram(url, base_dir):

    os.makedirs(base_dir, exist_ok=True)

    uid = str(uuid.uuid4())

    out = os.path.join(
        base_dir,
        f"{uid}.%(ext)s"
    )


    options = {

        "outtmpl": out,

        "format":
        "bv*+ba/best",

        "merge_output_format":
        "mp4",

        "noplaylist":
        True,

        "quiet":
        True,

        "no_warnings":
        True,

        "retries":
        15,

        "fragment_retries":
        15,

        "socket_timeout":
        60,

        "concurrent_fragment_downloads":
        5
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
            f"DOWNLOAD ERROR: {e}"
        )


    return None



# =========================
# VIDEO DURATION
# =========================

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


    except Exception:

        return 60



# =========================
# AUDIO EXTRACTION
# =========================

def extract_audio(video_path):

    base = video_path.rsplit(
        ".",
        1
    )[0]


    duration = get_duration(
        video_path
    )


    segment = 25


    points = set()


    # شروع ویدیو
    points.add(0)


    # نقاط هوشمند
    if duration > segment:

        step = max(
            20,
            duration / 6
        )


        current = 0

        while current < duration:

            points.add(
                max(
                    0,
                    current
                )
            )

            current += step



    # آخر ویدیو
    points.add(
        max(
            0,
            duration - segment
        )
    )


    points = sorted(
        list(points)
    )


    files = []


    for index, start in enumerate(points):

        audio = (
            f"{base}_music_{index}.wav"
        )


        try:

            subprocess.run(
                [
                    "ffmpeg",
                    "-y",

                    "-ss",
                    str(
                        int(start)
                    ),

                    "-i",
                    video_path,

                    "-t",
                    str(segment),

                    "-vn",

                    "-ac",
                    "1",

                    "-ar",
                    "44100",

                    "-af",
                    "loudnorm",

                    "-c:a",
                    "pcm_s16le",

                    audio
                ],

                stdout=subprocess.DEVNULL,

                stderr=subprocess.DEVNULL
            )


            if (
                os.path.exists(audio)
                and
                os.path.getsize(audio) > 20000
            ):

                files.append(
                    audio
                )


        except Exception as e:

            logging.error(
                f"AUDIO ERROR: {e}"
            )


    return files
