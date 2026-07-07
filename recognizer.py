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
            and os.path.getsize(path) > 15000
        )
    except:
        return False



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

                timeout=60
            )


        if response.status_code != 200:
            logging.warning(
                f"HTTP ERROR {response.status_code}"
            )
            return None


        return response.json()


    except Exception as e:

        logging.error(
            f"AUDD REQUEST ERROR: {e}"
        )

        return None



def extract_result(data):

    try:

        if not data:
            return None


        if data.get("status") != "success":
            return None


        result = data.get(
            "result"
        )


        if not result:
            return None


        artist = result.get(
            "artist"
        )

        title = result.get(
            "title"
        )


        if not artist or not title:
            return None


        return {

            "artist": artist,

            "title": title,

            "album": result.get(
                "album"
            ),

            "release_date": result.get(
                "release_date"
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
            f"RESULT ERROR: {e}"
        )

        return None



def recognize_audio(paths):


    if isinstance(paths, str):
        paths = [paths]


    audios = []


    for p in paths:

        if valid_audio(p):

            audios.append(p)



    if not audios:

        logging.info(
            "NO VALID AUDIO"
        )

        return None



    # فایل‌های بزرگ‌تر اول

    audios.sort(
        key=lambda x: os.path.getsize(x),
        reverse=True
    )



    for index, audio in enumerate(audios):


        logging.info(
            f"TRY AUDIO {index+1}/{len(audios)} : {audio}"
        )


        for retry in range(2):

            result = audd_request(
                audio
            )


            song = extract_result(
                result
            )


            if song:

                logging.info(
                    f"FOUND {song}"
                )

                return song



            time.sleep(1)



    logging.info(
        "MUSIC NOT FOUND"
    )


    return None
