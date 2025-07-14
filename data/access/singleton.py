class Singleton(type):  # Inherit from type DataAccess can be a singleton

    _instances = []  # class bassed attribute, shared across all instances 

    def __call__(cls, *args, **kwargs) -> type:
        if cls not in cls._instances:
            _instance = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances.append(_instance)
        return _instance