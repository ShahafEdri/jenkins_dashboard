import json
from datetime import datetime, timedelta
import os


class Cache:
    def __init__(self, cache_file, cache_expiry):
        self.cache_file = cache_file
        self.cache_expiry = timedelta(minutes=cache_expiry)
        self.cache_expity_delete = timedelta(days=1)

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
            try:
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    if key in cache:
                        time = cache[key]['time']
                        time = datetime.fromtimestamp(time)
                        if time + self.cache_expiry > datetime.now():
                            return False
            except json.decoder.JSONDecodeError:
                # delete cache file if it is not json format
                os.remove(self.cache_file)
        return True

    def __del__(self):
        self._delete_expired_cache()

    def __repr__(self):
        return f'Cache(cache_file={self.cache_file}, cache_expiry={self.cache_expiry})'

    def __str__(self):
        return f'Cache(cache_file={self.cache_file}, cache_expiry={self.cache_expiry})'

    def __getitem__(self, key):
        return self._get_cached_data(key)

    def __setitem__(self, key, value):
        self._cache_data(key, value)
