from replacementPolicy import LRUCache

class Ram:
    def __init__(self, capacity=10, block_size=4):
        self.capacity = capacity
        self.block_size = block_size
        self.data_cache = LRUCache(capacity)

    def get_data(self, key):
        return self.data_cache.get(key)

    def set_data(self, key, value):
        self.data_cache.set(key, value)


class HardDiskDrive:

    def __init__(self, capacity=10, block_size=128):
        self.capacity = capacity
        self.block_size = block_size
        self.data = {}

    def add_data(self, new_data):
        # Return the frequency to decide if we need to move to SSD
        frequency = 0
        if new_data in self.data:
            frequency = self.data[new_data] + 1
            self.data[new_data] = frequency
        else:
            self.data[new_data] = 1 # First insert, set the frequency to one
            frequency = 1

        return frequency

    def delete_data(self, data_key):
        del self.data[data_key]


class SolidStateDrive:

    def __init__(self, capacity=100, block_size=128):
        self.capacity = capacity
        self.block_size = block_size
        self.data_cache = LRUCache(capacity)

    def get_data(self, key):
        return self.data_cache.get(key)

    def set_data(self, key, value):
        self.data_cache.set(key, value)
