"""Step-level logging decorator. Complements the interaction-level tracing in traced.py."""

import functools
import logging
import time


logger = logging.getLogger("steps")


def log_step(func):
    """Logs step entry/exit with timing. Apply to pytest-bdd step defs."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        name = func.__name__
        logger.info("[Step] %s", name)
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.info("[Step] %s -> OK (%.0fms)", name, elapsed_ms)
            return result
        except Exception:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.error("[Step] %s -> FAILED (%.0fms)", name, elapsed_ms)
            raise

    return wrapper
