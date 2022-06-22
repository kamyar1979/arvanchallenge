import inspect
from functools import wraps, reduce
from multiprocessing.shared_memory import SharedMemory
from operator import xor
import struct
import time
import logging
import mmh3


def shared_memory_cache(shm_name: str, ttl: int = 0):
    shm = SharedMemory(shm_name)
    def decorate(func):
        sig = inspect.signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            logging.debug("Unpacking shared cache data")
            keys = struct.unpack_from('1000i', shm.buf[:4000], 0)
            logging.debug('Hashing parameters')
            h = reduce(xor, map(mmh3.hash, args))
            logging.debug("Checking if item exists in shared cache")
            if h in keys:
                ind = keys.index(h)
                logging.info('Item exists in shared cache with index %d.', ind)
                logging.debug('Checking storage time of item')
                epoch = struct.unpack_from('i', shm.buf[4000:8000], ind * 4)[0]
                logging.debug('Item is cached at %s', time.gmtime(epoch))
                if int(time.time()) - epoch < ttl:
                    logging.info('Item valid! Returning from shared cache.')
                    return str(struct.unpack_from('50c', shm.buf[8000:], ind * 50)[0], encoding='utf8')
                else:
                    logging.warning('Item expired!')
                    struct.pack_into('i', shm.buf[:4000], ind * 4, 0)

            logging.info('Calculating item...')
            result = func(*args, **kwargs)
            logging.info('Saving item in shared cache.')
            ind = keys.index(0)
            struct.pack_into('i', shm.buf[:4000], ind * 4, h)
            struct.pack_into(f'{len(result)}b', shm.buf[8000:], ind * 50, *iter(bytes(result, encoding='utf-8')))
            struct.pack_into('i', shm.buf[4000:8000], ind * 4, int(time.time()))
            return result

        wrapper.__name__ = func.__name__
        wrapper.__signature__ = sig

        return wrapper

    return decorate


