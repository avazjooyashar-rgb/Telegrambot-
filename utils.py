import os
import time

def safe_remove(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except:
        pass


class RateLimiter:
    def __init__(self, delay):
        self.delay = delay
        self.users = {}

    def allow(self, user_id):
        now = time.time()
        last = self.users.get(user_id, 0)

        if now - last < self.delay:
            return False

        self.users[user_id] = now
        return True
