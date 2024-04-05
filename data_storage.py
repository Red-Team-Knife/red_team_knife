import json


class DataStorage:
    def __init__(self, dataPath):
        self.__dataPath__ = dataPath
        self.__data__ = self.__load_data__()

    def __load_data__(self):
        try:
            with open(self.__dataPath__, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}
        return data

    def __save_data__(self):
        with open(self.__dataPath__, "w") as file:
            json.dump(self.__data__, file, indent=4)

    def save_key_value(self, key, value):
        self.__data__[key] = value
        self.__save_data__()

    def get_value(self, key):
        return self.__data__.get(key)
