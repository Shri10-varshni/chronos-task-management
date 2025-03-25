import redis
import json

class Cache:
    def __init__(self):
        self.client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def get(self, key: str):
        cached_data = self.client.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None

    def set(self, key: str, value: dict, ex: int = 3600):
        self.client.setex(key, ex, json.dumps(value))
