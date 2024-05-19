import os, utils.data_storage as data_storage, datetime, json


class Scan:

    def __init__(self, name=None, host=None, protocol=None, resource=None, root_folder=None, file_source=None):

        if file_source is not None:
            self.data_storage = data_storage.DataStorage(file_source)
            self.date = self.data_storage.get_value("creation_date")
            self.time = self.data_storage.get_value("creation_time")
            self.name = self.data_storage.get_value("name")
            self.host = self.data_storage.get_value("host")
            self.protocol = self.data_storage.get_value("protocol")
            self.resource = self.data_storage.get_value("resource")

        elif (
            name is not None
            and host is not None
            and protocol is not None
            and resource is not None
            and root_folder is not None
            and file_source is None
        ):
            self.root_folder = root_folder
            self.date = datetime.datetime.now().date()
            self.time = datetime.datetime.now().time()
            self.name = name
            self.host = host
            self.protocol = protocol
            self.resource = resource
            self.data_storage = data_storage.DataStorage(
                self.root_folder + f"/{str(self.date) + str(self.time)}.json"
            )
            self.data_storage.save_key_value("creation_date", str(self.date))
            self.data_storage.save_key_value("creation_time", str(self.time))
            self.data_storage.save_key_value("host", self.host)
            self.data_storage.save_key_value("name", self.name)
            self.data_storage.save_key_value("protocol", self.protocol)
            self.data_storage.save_key_value("resource", self.resource)

    def save_scan(self, tool_name, data):
        self.data_storage.save_key_value(tool_name, data)
        return

    def get_tool_scan(self, tool:str):
        
        return self.data_storage.get_value(tool)
