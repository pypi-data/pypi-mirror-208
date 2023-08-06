import numpy as np
from typing import List
import logging
import ray
import os
import psutil
import gc


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s: %(message)s",
    datefmt="%y-%m-%d %H:%M:%S"
)

PCT_CPU = float(os.environ.get("B2I8_PCT_CPU", "0.9"))
NUM_CPU = os.environ.get("B2I8_NUM_CPU")
if NUM_CPU is None:
    NUM_CPU = max(1, int(psutil.cpu_count(logical=False) * PCT_CPU))
ray.init(num_cpus=NUM_CPU)


@ray.remote
def bool_to_int8_cpu(hashvalues: List[List[bool]]) -> List[List[np.int8]]:
    s = []
    for h in hashvalues:
        s.append(np.packbits(
            h.reshape(-1, 8),
            bitorder='big').astype(np.int8))
    return np.vstack(s)


@ray.remote
def int8_to_bool_cpu(serialized: List[List[np.int8]]) -> List[List[bool]]:
    h = []
    for s in serialized:
        h.append(np.unpackbits(
            s.astype(np.uint8),
            bitorder='big').reshape(-1))
    return np.vstack(h)


def bool_to_int8_batch(hashvalues: List[List[bool]]) -> List[List[np.int8]]:
    if (hashvalues.shape[0] % NUM_CPU) == 0:
        bsz = hashvalues.shape[0] // NUM_CPU
    else:
        bsz = hashvalues.shape[0] // (NUM_CPU - 1)
    if bsz == 0:
        bsz = 1
    pool_size = min(NUM_CPU, hashvalues.shape[0])
    try:
        return np.vstack(ray.get([
            bool_to_int8_cpu.remote(hashvalues[(i * bsz):((i + 1) * bsz)])
            for i in range(pool_size)])).astype(np.int8)
    except Exception as e:
        logger.error(e)
        ray.shutdown()
        gc.collect()


def int8_to_bool_batch(serialized: List[List[np.int8]]) -> List[List[bool]]:
    if (serialized.shape[0] % NUM_CPU) == 0:
        bsz = serialized.shape[0] // NUM_CPU
    else:
        bsz = serialized.shape[0] // (NUM_CPU - 1)
    if bsz == 0:
        bsz = 1
    pool_size = min(NUM_CPU, serialized.shape[0])
    try:
        return np.vstack(ray.get([
            int8_to_bool_cpu.remote(serialized[(i * bsz):((i + 1) * bsz)])
            for i in range(pool_size)])).astype(np.uint8)
    except Exception as e:
        logger.error(e)
        ray.shutdown()
        gc.collect()
