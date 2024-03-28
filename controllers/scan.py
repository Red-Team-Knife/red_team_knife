import os, json

class ScanController:
    
    def __init__(self):
        self.root_folder = 'scan_archive'
    

    def create_folder(self, folder_name):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            return os.path.abspath(folder_name)
        else:
            return None
        
    def create_file(self, folder_name):
        folder_path = os.path.abspath(folder_name)
        file_path = os.path.join(folder_path, "scan.json")
        
        if not os.path.exists(folder_path):
            return None
        
        with open(file_path, 'w') as file:
            file.write('{}')
        
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
    
    def get_scan(self, folder_name):
        folder_path = os.path.abspath(folder_name)

        
        if not os.path.exists(folder_path):
            return None
        
        # Fetching all files in dir
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            
            # Check if file is JSON
            if os.path.isfile(file_path) and str(file_name).endswith('.json'):

                # Read file
                with open(file_path, 'r') as file:
                    try:
                        scan = json.load(file)
                        return scan
                    except json.JSONDecodeError as e:
                        print(f"Error during fetch of the scan '{file_name}': {e}")
                        return None





