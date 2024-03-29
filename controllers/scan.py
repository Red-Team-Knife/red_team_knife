import os, json

class ScanController:
    
    def __init__(self):
        self.root_folder = 'scan_archive'
    

    def create_root_folder(self):
        folder_path = os.path.abspath(self.root_folder)
        if not os.path.exists(folder_path):
            os.makedirs(self.root_folder)
            return os.path.abspath(folder_path)
        else:
            return None
        
    def create_file(self, file_name):
        root_path = os.path.abspath(self.root_folder)

        if not os.path.exists(root_path):
            self.create_root_folder()
        
        
        file_path = os.path.join(root_path, file_name + ".json") 

        with open(file_path, 'w') as file:
            json.dump({file_name: ''}, file)
        
        return file_path

    def fetch_saved_scans(self):
        root_path = os.path.abspath(self.root_folder)

        if not os.path.exists(root_path):
            return None
        
        # List all saved scans
        folders = []

        for folder in os.listdir(root_path):
            folders.append(folder)

        return folders
    
    def get_scan(self, scan_name):
        root_path = os.path.abspath(self.root_folder)
        
        if not os.path.exists(root_path):
            return None
        
        file_path = os.path.join(root_path, f"{scan_name}.json")

        # Check if file exists
        if os.path.isfile(file_path):
                            # Read file
                with open(file_path, 'r') as file:
                    try:
                        scan = json.load(file)
                        return scan
                    except json.JSONDecodeError as e:
                        print(f"Error during fetch of the scan '{scan_name}': {e}")
                        return None
        else:
            return None








