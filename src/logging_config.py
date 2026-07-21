import contextlib
import logging
import sys
import time


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )


@contextlib.contextmanager
def log_timer(logger: logging.Logger, stage: str):
    """Context manager: log *stage* duration on exit, even on exception."""
    t0 = time.perf_counter()
    try:
        yield
    finally:
        elapsed = (time.perf_counter() - t0) * 1000
        logger.info("[timing] %s — %.0fms", stage, elapsed)
