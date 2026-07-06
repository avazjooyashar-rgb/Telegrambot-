import yt_dlp
import uuid
import os
import subprocess


def download_instagram(url, base_dir):
    uid = str(uuid.uuid4())
    out = os.path.join(base_dir, f"{uid}.mp4")

    ydl_opts = {
        "outtmpl": out,
        "format": "bv*+ba/best",
        "merge_output_format": "mp4",
        "quiet": True,
        "noplaylist": True,
        "retries": 10,
        "fragment_retries": 10,
        "socket_timeout": 60
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return out



def get_duration(video):
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
                video
            ],
            capture_output=True,
            text=True
        )

        return float(result.stdout.strip())

    except:
        return 60



def extract_audio(video_path):

    base = video_path.rsplit(".", 1)[0]

    duration = get_duration(video_path)

    points = [
        0,
        max(0, duration / 3 - 12),
        max(0, duration / 2 - 12),
        max(0, duration - 25)
    ]

    files = []


    for i, start in enumerate(points):

        audio = f"{base}_audio_{i}.mp3"

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                str(int(start)),
                "-i",
                video_path,
                "-t",
                "25",
                "-vn",

                "-ac",
                "2",

                "-ar",
                "44100",

                "-af",
                "loudnorm",

                "-codec:a",
                "libmp3lame",

                "-b:a",
                "320k",

                audio
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


        if os.path.exists(audio) and os.path.getsize(audio) > 10000:
            files.append(audio)


    return files



def download_music(query, base_dir):

    uid = str(uuid.uuid4())

    out = os.path.join(
        base_dir,
        f"{uid}.%(ext)s"
    )


    ydl_opts = {
        "format": "bestaudio/best",

        "outtmpl": out,

        "quiet": True,

        "noplaylist": True,

        "retries": 10,

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",

                "preferredcodec": "mp3",

                "preferredquality": "320"
            }
        ]
    }


    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        ydl.download(
            [
                f"ytsearch1:{query}"
            ]
        )


    for f in os.listdir(base_dir):

        if f.startswith(uid) and f.endswith(".mp3"):

            return os.path.join(base_dir, f)


    return None
