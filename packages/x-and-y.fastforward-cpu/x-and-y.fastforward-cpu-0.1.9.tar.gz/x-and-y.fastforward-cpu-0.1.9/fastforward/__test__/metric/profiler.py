import psutil


class Profiler:

    def __init__(self, profile_memory: bool = True):
        self.profile_memory = profile_memory

    def __enter__(self):
        self.current = psutil.virtual_memory().used

    def __exit__(self, exc_type, exc_val, exc_tb):
        memory_consumption = (psutil.virtual_memory().used - self.current) / 1024 / 1024

        if self.profile_memory:
            print("memory consumption: " + str(memory_consumption))
