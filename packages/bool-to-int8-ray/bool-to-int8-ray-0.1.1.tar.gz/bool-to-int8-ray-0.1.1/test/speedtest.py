# run `pip install .` first
from bool_to_int8_ray import bool_to_int8_batch, int8_to_bool_batch
import numpy as np
from typing import List
from timeit import default_timer as timer
import logging
import ray
import gc


# start logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# simple CPU version
def bool_to_int8_cpu(hashvalues: List[List[bool]]) -> List[List[np.int8]]:
    s = []
    for h in hashvalues:
        s.append(np.packbits(
            h.reshape(-1, 8),
            bitorder='big').astype(np.int8))
    return np.vstack(s)


def int8_to_bool_cpu(serialized: List[List[np.int8]]) -> List[List[bool]]:
    h = []
    for s in serialized:
        h.append(np.unpackbits(
            s.astype(np.uint8),
            bitorder='big').reshape(-1))
    return np.vstack(h)


# test data
hashvalues = (np.random.normal(size=(2 * (10**6), 1024)) > 0).astype(np.uint8)

# numpy experiment
start = timer()
serialized1 = bool_to_int8_cpu(hashvalues)
print(f"{timer() - start: .6f} -- numpy version, hash to int8")

start = timer()
deserialized1 = int8_to_bool_cpu(serialized1)
print(f"{timer() - start: .6f} -- numpy version, int8 to hash")
del serialized1, deserialized1

# ray.io experiment
start = timer()
serialized2 = bool_to_int8_batch(hashvalues)
print(f"{timer() - start: .6f} -- ray.io version, hash to int8")

start = timer()
deserialized2 = int8_to_bool_batch(serialized2)
print(f"{timer() - start: .6f} -- ray.io version, int8 to hash")
del serialized2, deserialized2

# done
ray.shutdown()
gc.collect()
