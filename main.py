from multiprocessing import Pool
from multiprocessing.managers import SharedMemoryManager
from functools import partial

from processor import process


if __name__ == "__main__":
    with SharedMemoryManager() as smm, Pool(10) as p, open('access.log', 'rt') as f, open('out.log', 'wt') as o:
        shm = smm.SharedMemory(size=58000)
        func = partial(process, shm.name)
        o.writelines(p.map(func, f))
