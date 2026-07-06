import requests
from config import AUDD_API

def recognize_audio(path):
    try:
        with open(path, "rb") as f:
            r = requests.post(
                "https://api.audd.io/",
                data={"api_token": AUDD_API},
                files={"file": f},
                timeout=30
            )

        data = r.json()

        if data.get("status") == "success":
            result = data.get("result")
            if result:
                return result["artist"], result["title"]

    except:
        pass

    return None
