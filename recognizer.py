import requests
import os
import time
import logging
from config import AUDD_API


logging.basicConfig(
    filename="recognizer.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


AUDD_URL = "https://api.audd.io/"


def valid_audio(path):
    try:
        return (
            os.path.exists(path)
            and os.path.getsize(path) > 8000
        )
    except:
        return False



def audd_request(path):

    try:
        with open(path, "rb") as audio:

            r = requests.post(
                AUDD_URL,
                data={
                    "api_token": AUDD_API,
                    "return": "spotify,apple_music"
                },
                files={
                    "file": audio
                },
                timeout=60
            )

        if r.status_code != 200:
            return None

        return r.json()

    except Exception as e:
        logging.error(f"REQUEST ERROR: {e}")
        return None



def extract_result(data):

    try:

        if not data:
            return None

        if data.get("status") != "success":
            return None

        result = data.get("result")

        if not result:
            return None


        artist = result.get("artist")
        title = result.get("title")


        if not artist or not title:
            return None


        return {
            "artist": artist,
            "title": title,
            "album": result.get("album"),
            "release_date": result.get("release_date"),
            "spotify": result.get("spotify"),
            "apple_music": result.get("apple_music")
        }


    except Exception as e:
        logging.error(f"RESULT ERROR: {e}")
        return None



def recognize_audio(paths):

    if isinstance(paths, str):
        paths = [paths]


    paths = [
        p for p in paths
        if valid_audio(p)
    ]


    if not paths:
        return None


    # فایل‌های قوی‌تر اول
    paths.sort(
        key=lambda x: os.path.getsize(x),
        reverse=True
    )


    # سه دور کامل تست
    for attempt in range(3):

        for audio in paths:

            logging.info(
                f"TRY {attempt+1}: {audio}"
            )


            response = audd_request(audio)

            song = extract_result(response)


            if song:
                logging.info(
                    f"FOUND: {song}"
                )
                return song


            time.sleep(2)


        time.sleep(3)


    logging.info("NO RESULT")

    return None
