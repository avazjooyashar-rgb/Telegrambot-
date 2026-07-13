import os
import json
import hashlib
import logging
import requests

from concurrent.futures import ThreadPoolExecutor, as_completed

from config import (
    AUDD_API,
    ACR_HOST,
    ACR_ACCESS_KEY,
    ACR_ACCESS_SECRET
)

from audio_processor import prepare_audio

from database import (
    get_song,
    save_song
)


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

            with open(
                CACHE_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

    except Exception as e:
        logging.error(e)

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
        logging.error(e)




def file_hash(path):

    try:

        h = hashlib.md5()

        with open(
            path,
            "rb"
        ) as f:

            for chunk in iter(
                lambda: f.read(4096),
                b""
            ):

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




def acr_request(path):

    try:

        from pyacrcloud import ACRCloudRecognizer


        config = {

            "host": ACR_HOST,

            "access_key": ACR_ACCESS_KEY,

            "access_secret": ACR_ACCESS_SECRET,

            "timeout": 10

        }


        acr = ACRCloudRecognizer(config)


        response = acr.recognize_by_file(
            path,
            0
        )


        return json.loads(response)


    except Exception as e:

        logging.error(
            f"ACR ERROR {e}"
        )


    return None




def audd_request(path):

    try:

        with open(
            path,
            "rb"
        ) as audio:

            response = requests.post(

                AUDD_URL,

                data={

                    "api_token": AUDD_API,

                    "return":
                    "spotify,apple_music"

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
            f"AUDD ERROR {e}"
        )


    return None
    def parse(data):

    try:

        if not data:
            return None


        # ACRCloud format
        if "status" in data:

            metadata = data.get(
                "metadata",
                {}
            )


            music = metadata.get(
                "music"
            )


            if music:

                item = music[0]


                artist = ""

                title = ""


                artists = item.get(
                    "artists",
                    []
                )


                if artists:

                    artist = artists[0].get(
                        "name",
                        ""
                    )


                title = item.get(
                    "title",
                    ""
                )


                if artist and title:

                    return {

                        "artist": artist,

                        "title": title,

                        "album": item.get(
                            "album",
                            {}
                        ).get(
                            "name"
                        ),

                        "spotify": None,

                        "apple_music": None

                    }



        # AudD format
        result = data.get(
            "result"
        )


        if result:

            artist = result.get(
                "artist"
            )


            title = result.get(
                "title"
            )


            if artist and title:

                return {

                    "artist": artist,

                    "title": title,

                    "album": result.get(
                        "album"
                    ),

                    "spotify": result.get(
                        "spotify"
                    ),

                    "apple_music": result.get(
                        "apple_music"
                    )

                }


    except Exception as e:

        logging.error(
            f"PARSE ERROR {e}"
        )


    return None





def recognize_audio(paths):


    if isinstance(
        paths,
        str
    ):

        paths = [paths]



    processed = []



    for item in paths:


        ready = prepare_audio(
            item
        )


        if valid_audio(
            ready
        ):

            processed.append(
                ready
            )



    if not processed:

        return None



    cache = load_cache()



    for file in processed:


        h = file_hash(
            file
        )


        if not h:
            continue



        # database check

        db_result = get_song(
            h
        )


        if db_result:

            logging.info(
                "DATABASE HIT"
            )

            return db_result




        # old json cache

        if h in cache:

            logging.info(
                "CACHE HIT"
            )

            return cache[h]





    # first ACRCloud

    for file in processed:


        logging.info(
            "TRY ACR"
        )


        result = parse(
            acr_request(file)
        )


        if result:


            h = file_hash(
                file
            )


            result["hash"] = h


            save_song(
                result
            )


            cache[h] = result


            save_cache(
                cache
            )


            logging.info(
                "ACR SUCCESS"
            )


            return result





    # fallback AudD

    for file in processed:


        logging.info(
            "TRY AUDD"
        )


        result = parse(
            audd_request(file)
        )


        if result:


            h = file_hash(
                file
            )


            result["hash"] = h


            save_song(
                result
            )


            cache[h] = result


            save_cache(
                cache
            )


            logging.info(
                "AUDD SUCCESS"
            )


            return result




    logging.info(
        "NO RESULT"
    )


    return None
