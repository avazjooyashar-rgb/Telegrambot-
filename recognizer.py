import requests
import os
import json
import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import AUDD_API


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
    except:
        pass
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
    except:
        return None


def valid_audio(path):
    return (
        os.path.exists(path)
        and os.path.getsize(path) > 10000
    )


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

                timeout=20
            )


        if r.status_code == 200:
            return r.json()

    except Exception as e:
        logging.error(
            f"AUDD {e}"
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


    except:
        pass


    return None



def recognize_audio(paths):

    if isinstance(paths, str):
        paths = [paths]


    files = [
        x for x in paths
        if valid_audio(x)
    ]


    if not files:
        return None


    cache = load_cache()


    for f in files:

        h = file_hash(f)

        if h in cache:
            logging.info("CACHE HIT")
            return cache[h]



    # چند نمونه همزمان بررسی می‌شوند
    with ThreadPoolExecutor(
        max_workers=min(3, len(files))
    ) as ex:


        jobs = [
            ex.submit(
                audd_request,
                f
            )
            for f in files
        ]


        for job in as_completed(jobs):

            result = parse(
                job.result()
            )


            if result:

                h = file_hash(files[0])

                if h:
                    cache[h] = result
                    save_cache(cache)


                logging.info(
                    f"FOUND {result}"
                )

                return result


    return None
