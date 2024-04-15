import os, utils.data_storage as data_storage, datetime, json


class Scan:

    def __init__(self, name=None, host=None, root_folder=None, file_source=None):

        if file_source is not None:
            self.data_storage = data_storage.DataStorage(file_source)
            self.date = self.data_storage.get_value("creation_date")
            self.time = self.data_storage.get_value("creation_time")
            self.name = self.data_storage.get_value("name")
            self.host = self.data_storage.get_value("host")

        elif (
            name is not None
            and host is not None
            and root_folder is not None
            and file_source is None
        ):
            self.root_folder = root_folder
            self.date = datetime.datetime.now().date()
            self.time = datetime.datetime.now().time()
            self.name = name
            self.host = host
            self.data_storage = data_storage.DataStorage(
                self.root_folder + f"/{str(self.date) + str(self.time)}.json"
            )
            self.data_storage.save_key_value("creation_date", str(self.date))
            self.data_storage.save_key_value("creation_time", str(self.time))
            self.data_storage.save_key_value("host", self.host)
            self.data_storage.save_key_value("name", self.name)

    def save_scan(self, tool_name, data):
        self.data_storage.save_key_value(tool_name, data)
        return

    def create_scan(self, file_name):
        if not os.path.exists(self.root_path):
            self.create_root_folder()

        if file_name is None:
            file_path = os.path.join(self.root_path, file_name)
        else:
            file_path = os.path.join(
                self.root_path,
            )

        with open(file_path, "w") as file:
            json.dump(
                {
                    file_name: {
                        "creation_date": datetime.datetime.now().date(),
                        "creation_time": datetime.datetime.now().time(),
                    }
                },
                file,
            )

        return file_path

    def get_tool_scan(self, tool:str):
        
        return self.data_storage.get_value(tool)
