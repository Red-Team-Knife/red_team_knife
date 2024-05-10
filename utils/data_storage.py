import json
import os


class DataStorage:
    def __init__(self, dataPath):
        self.__dataPath__ = dataPath
        self.data = self.__load_data__()

    def __load_data__(self):
        try:
            with open(self.__dataPath__, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}
        return data

    def __save_data__(self):
        with open(self.__dataPath__, "w") as file:
            os.chmod(self.__dataPath__, 0o777)
            json.dump(self.data, file, indent=4)

    def save_key_value(self, key, value):
        self.data[key] = value
        self.__save_data__()

    def get_value(self, key):
        return self.data.get(key)
