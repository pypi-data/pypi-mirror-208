import threading
from typing import Callable

__all__ = ["fire_and_forget"]


def fire_and_forget(func: Callable):
    threading.Thread(target=func).start()
