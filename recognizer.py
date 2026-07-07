import requests
import os
import time
import logging
import hashlib
import json

from config import AUDD_API


logging.basicConfig(
    filename="recognizer.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


AUDD_URL = "https://api.audd.io/"
CACHE_FILE = "music_cache.json"


# =========================
# CACHE
# =========================

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
        with open(
            CACHE_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception as e:
        logging.error(
            f"CACHE SAVE ERROR {e}"
        )



def file_hash(path):

    try:

        h = hashlib.md5()

        with open(path,"rb") as f:

            for chunk in iter(
                lambda:f.read(4096),
                b""
            ):
                h.update(chunk)

        return h.hexdigest()

    except:

        return None



# =========================
# VALIDATION
# =========================

def valid_audio(path):

    try:

        return (
            os.path.exists(path)
            and os.path.getsize(path) > 15000
        )

    except:

        return False



# =========================
# AUDD REQUEST
# =========================

def audd_request(path):

    try:

        with open(path,"rb") as audio:

            r = requests.post(

                AUDD_URL,

                data={
                    "api_token": AUDD_API,
                    "return":
                    "spotify,apple_music"
                },

                files={
                    "file": audio
                },

                timeout=60
            )


        if r.status_code != 200:

            logging.warning(
                f"AUDD HTTP {r.status_code}"
            )

            return None


        return r.json()


    except Exception as e:

        logging.error(
            f"AUDD ERROR {e}"
        )

        return None



# =========================
# PARSE RESULT
# =========================

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

            "album":
            result.get("album"),

            "release_date":
            result.get("release_date"),

            "spotify":
            result.get("spotify"),

            "apple_music":
            result.get("apple_music")

        }


    except Exception as e:

        logging.error(
            f"PARSE ERROR {e}"
        )

        return None



# =========================
# MAIN RECOGNIZER
# =========================

def recognize_audio(paths):


    if isinstance(paths,str):

        paths=[paths]


    files=[]


    for p in paths:

        if valid_audio(p):

            files.append(p)



    if not files:

        logging.info(
            "NO AUDIO"
        )

        return None



    cache=load_cache()



    # فایل‌های بهتر اول

    files.sort(
        key=lambda x:
        os.path.getsize(x),
        reverse=True
    )



    for audio in files:


        h=file_hash(audio)


        if h and h in cache:

            logging.info(
                "CACHE HIT"
            )

            return cache[h]



        logging.info(
            f"TRY {audio}"
        )



        # چند تلاش برای هر نمونه

        for attempt in range(3):


            result=audd_request(
                audio
            )


            song=extract_result(
                result
            )


            if song:


                logging.info(
                    f"FOUND {song}"
                )


                if h:

                    cache[h]=song

                    save_cache(
                        cache
                    )


                return song



            time.sleep(
                2
            )



    logging.info(
        "NOT FOUND"
    )


    return None
