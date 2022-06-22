import logging.config

from cache_decorator import shared_memory_cache

logging.config.fileConfig('logging.ini')


def process(shm_name: str, s: str) -> str:
    @shared_memory_cache(shm_name=shm_name, ttl=30)
    def heavy_computational_function(s: str) -> str:
        def result_iterator():
            for ch in s:
                yield ch
                yield str(sum(1 for c in s if c == ch))

        return ''.join(result_iterator())
    return heavy_computational_function(s)




