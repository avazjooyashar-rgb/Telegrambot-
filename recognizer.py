import requests
import os
import json
import hashlib
import logging

from concurrent.futures import ThreadPoolExecutor, as_completed

from config import AUDD_API
from audio_processor import prepare_audio


logging.basicConfig(
    filename="recognizer.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


AUDD_URL = "https://api.audd.io/"
CACHE_FILE = "music_cache.json"


def load_cache():
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logging.error(e)

    return {}



def save_cache(data):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception as e:
        logging.error(e)



def file_hash(path):
    try:
        h = hashlib.md5()

        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)

        return h.hexdigest()

    except Exception:
        return None



def valid_audio(path):

    return (
        path
        and os.path.exists(path)
        and os.path.getsize(path) > 10000
    )



def audd_request(path):

    try:

        with open(path, "rb") as audio:

            response = requests.post(
                AUDD_URL,

                data={
                    "api_token": AUDD_API,
                    "return": "spotify,apple_music"
                },

                files={
                    "file": audio
                },

                timeout=20
            )


        if response.status_code == 200:
            return response.json()


    except Exception as e:
        logging.error(
            f"AUDD ERROR: {e}"
        )


    return None



def parse(data):

    try:

        if not data:
            return None


        result = data.get("result")

        if not result:
            return None


        artist = result.get("artist")
        title = result.get("title")


        if artist and title:

            return {
                "artist": artist,
                "title": title,
                "album": result.get("album"),
                "spotify": result.get("spotify"),
                "apple_music": result.get("apple_music")
            }


    except Exception as e:
        logging.error(e)


    return None



def recognize_audio(paths):

    if isinstance(paths, str):
        paths = [paths]


    # آماده سازی فایل‌ها
    processed = []

    for item in paths:

        ready = prepare_audio(item)

        if valid_audio(ready):
            processed.append(ready)


    if not processed:
        return None


    cache = load_cache()


    for file in processed:

        h = file_hash(file)

        if h and h in cache:

            logging.info("CACHE HIT")

            return cache[h]



    with ThreadPoolExecutor(
        max_workers=min(3, len(processed))
    ) as executor:


        tasks = {
            executor.submit(
                audd_request,
                file
            ): file

            for file in processed
        }


        for task in as_completed(tasks):

            source_file = tasks[task]

            result = parse(
                task.result()
            )


            if result:

                h = file_hash(source_file)

                if h:

                    cache[h] = result
                    save_cache(cache)


                logging.info(
                    f"FOUND {result}"
                )


                return result



    logging.info("NOT FOUND")

    return None
