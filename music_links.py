import urllib.parse


def google_search(artist, title):
    query = f"{artist} {title}"

    return (
        "https://www.google.com/search?q="
        + urllib.parse.quote(query)
    )



def youtube_search(artist, title):
    query = f"{artist} {title}"

    return (
        "https://www.youtube.com/results?search_query="
        + urllib.parse.quote(query)
    )



def spotify_search(artist, title):
    query = f"{artist} {title}"

    return (
        "https://open.spotify.com/search/"
        + urllib.parse.quote(query)
    )



def apple_music_search(artist, title):
    query = f"{artist} {title}"

    return (
        "https://music.apple.com/us/search?term="
        + urllib.parse.quote(query)
    )



def build_links(result):

    if not result:
        return None


    artist = result.get("artist")
    title = result.get("title")


    return {
        "google": google_search(
            artist,
            title
        ),

        "youtube": youtube_search(
            artist,
            title
        ),

        "spotify": (
            result.get("spotify")
            or spotify_search(
                artist,
                title
            )
        ),

        "apple_music": (
            result.get("apple_music")
            or apple_music_search(
                artist,
                title
            )
        )
    }
