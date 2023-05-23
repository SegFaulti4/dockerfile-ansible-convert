import multiprocessing
import parts
from typing import List, Callable


def log_header(s: str) -> str:
    return f"{s.upper()}:"


def flag_print(*args, **kwargs):
    if "echo" in kwargs and kwargs["echo"]:
        del kwargs["echo"]
        print(*args, **kwargs)


def map_reduce(worker: Callable, data: List[str], n_proc: int, log_dir: str) -> List[str]:
    echo = False
    with multiprocessing.Pool(processes=n_proc) as pool:
        spans = parts.parts(data, n_proc)
        per_proc = pool.map(worker, [(list(span), idx, echo, log_dir) for span, idx in zip(spans, range(n_proc))])
        res = [good_run for p in per_proc for good_run in p]
    return res
