# create singleton class to be used as meta class
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        # check if instance is already created
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        # return instance
        return cls._instances[cls]