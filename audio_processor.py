import os
import subprocess
import uuid
import logging


logging.basicConfig(
    filename="audio_processor.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def extract_audio(video_path):
    """
    تبدیل ویدیو به mp3 با کیفیت مناسب
    """

    try:
        output = f"/tmp/{uuid.uuid4()}.mp3"

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-vn",
            "-ac",
            "2",
            "-ar",
            "44100",
            "-b:a",
            "192k",
            output
        ]

        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30
        )

        if os.path.exists(output):
            return output

    except Exception as e:
        logging.error(e)

    return None



def cut_audio(audio_path, seconds=30):

    try:
        output = f"/tmp/{uuid.uuid4()}_cut.mp3"

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            audio_path,
            "-ss",
            "0",
            "-t",
            str(seconds),
            "-c",
            "copy",
            output
        ]

        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if os.path.exists(output):
            return output

    except Exception as e:
        logging.error(e)

    return audio_path



def prepare_audio(file):

    if file.endswith((".mp4", ".mkv", ".webm")):
        file = extract_audio(file)

    if file:
        file = cut_audio(file)

    return file
