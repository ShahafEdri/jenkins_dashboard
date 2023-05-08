import json
from datetime import datetime, timedelta
import os


class Cache:
    def __init__(self, cache_file, cache_expiry):
        self.cache_file = cache_file
        self.cache_expiry = timedelta(minutes=cache_expiry)
        self.cache_expity_delete = timedelta(days=1)
        self._delete_expired_cache()  # delete expired cache when init

    def _delete_expired_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
                for key in list(cache.keys()):
                    time = cache[key]['time']
                    time = datetime.fromtimestamp(time)
                    if time + self.cache_expity_delete < datetime.now():
                        del cache[key]
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f)

    def cache_data(self, key: str, data) -> None:
        self._cache_data(key, data)

    def _cache_data(self, key: str, data) -> None:
        # save the cache by url as key and time and data as value
        # if the cache is expired
        cache = {
            key: {
                'time': datetime.now().timestamp(),
                'data': data
            }
        }
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                # check if the cache file is json format
                try:
                    new_cache = json.load(f)
                    new_cache.update(cache)
                except json.decoder.JSONDecodeError:
                    new_cache = cache
        else:
            new_cache = cache
        with open(self.cache_file, 'w') as f:
            json.dump(new_cache, f)

    def get_cached_data(self, key):
        return self._get_cached_data(key)

    def _get_cached_data(self, key):
        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
                return cache[key]['data']
        except (FileNotFoundError, KeyError):
            return None

    def is_cache_expired(self, key):
        return self._is_cache_expired(key)

    def _is_cache_expired(self, key):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
                if key in cache:
                    time = cache[key]['time']
                    time = datetime.fromtimestamp(time)
                    if time + self.cache_expiry > datetime.now():
                        return False
        return True
