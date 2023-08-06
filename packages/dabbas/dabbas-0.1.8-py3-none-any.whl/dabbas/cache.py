import threading
import os
import inspect
import hashlib
import pickle


def cache(force=False, src=True, path=None):
    lock = threading.Lock()

    def decorator(func):
        # if src:
        #     cache_key = hashlib.sha256()
        #     cache_key.update(pickle.dumps(inspect.getsource(func)))
        #     cache_key = cache_key.hexdigest()
        #     cache_path = path if path is not None else '.func_cache/{}-{}'.format(
        #         func.__name__, cache_key)
        # else:
        cache_path = path if path is not None else '.func_cache/{}'.format(
            func.__name__)

        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as f:
                local_cache = pickle.load(f)
        else:
            local_cache = {}

        def wrapper(*args, **kwargs):
            cache_key = hashlib.sha256()
            if src:
                cache_key.update(pickle.dumps(inspect.getsource(func)))
            else:
                cache_key.update(pickle.dumps(func.__name__))
            cache_key.update(pickle.dumps(args))
            cache_key.update(pickle.dumps(kwargs))

            cache_key = cache_key.hexdigest()

            with lock:
                if not force and cache_key in local_cache:
                    return local_cache[cache_key]

            result = func(*args, **kwargs)

            with lock:
                local_cache[cache_key] = result

                if not os.path.exists('.func_cache'):
                    os.makedirs('.func_cache')

                with open(cache_path, 'wb') as f:
                    pickle.dump(local_cache, f)

            return result

        def get_cached(*args, **kwargs):
            cache_key = hashlib.sha256()
            if src:
                cache_key.update(pickle.dumps(inspect.getsource(func)))
            else:
                cache_key.update(pickle.dumps(func.__name__))
            cache_key.update(pickle.dumps(args))
            cache_key.update(pickle.dumps(kwargs))

            cache_key = cache_key.hexdigest()

            with lock:
                if not force and cache_key in local_cache:
                    return local_cache[cache_key]

            return None

        wrapper.get_cached = get_cached
        wrapper.cache_path = cache_path
        wrapper.cache = local_cache
        wrapper.lock = lock
        return wrapper

    return decorator
