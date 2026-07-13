import sqlite3
import os
from datetime import datetime


DB_FILE = "music_database.db"


def get_connection():
    return sqlite3.connect(DB_FILE)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT UNIQUE,
        artist TEXT,
        title TEXT,
        album TEXT,
        spotify TEXT,
        apple_music TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()



def save_song(data):

    if not data or "hash" not in data:
        return

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        INSERT OR REPLACE INTO songs
        (
            hash,
            artist,
            title,
            album,
            spotify,
            apple_music,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("hash"),
            data.get("artist"),
            data.get("title"),
            data.get("album"),
            data.get("spotify"),
            data.get("apple_music"),
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

    except Exception as e:
        print("DB SAVE ERROR:", e)



def get_song(file_hash):

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM songs WHERE hash=?",
            (file_hash,)
        )

        row = cur.fetchone()
        conn.close()

        if row:
            return {
                "artist": row[2],
                "title": row[3],
                "album": row[4],
                "spotify": row[5],
                "apple_music": row[6]
            }

    except Exception as e:
        print("DB READ ERROR:", e)

    return None
