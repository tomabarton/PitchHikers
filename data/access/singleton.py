# Inherit from type DataAccess can be a singleton
# NOT thread safe, should use lock
from threading import Lock
from typing import Any

class Singleton(type):

    _instances: dict[type,type] = {}
    _lock = Lock()

    def __call__(cls, *args: tuple[Any], **kwargs: tuple[Any]) -> type:
        with cls._lock:
            if cls not in cls._instances:  # Overlap between type and singleton?
                _instance = super(Singleton, cls).__call__(*args, **kwargs)
                cls._instances[cls] = _instance
            return cls._instances[cls]
