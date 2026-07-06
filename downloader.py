import yt_dlp
import uuid
import os
import subprocess

def download_instagram(url, base_dir):
    uid = str(uuid.uuid4())
    out = f"{base_dir}/{uid}.mp4"

    ydl_opts = {
        "outtmpl": out,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "quiet": True,
        "noplaylist": True,
        "retries": 5
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return out


def extract_audio(video_path, seconds=25):
    audio_path = video_path.replace(".mp4", ".mp3")

    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-t", str(seconds),
        "-vn",
        "-ab", "192k",
        audio_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return audio_path


def download_music(query, base_dir):
    uid = str(uuid.uuid4())
    out = f"{base_dir}/{uid}.mp3"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out,
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch1:{query}"])

    return out
