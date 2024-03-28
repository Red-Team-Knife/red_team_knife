LINK_NMAP_INTERFACE = "/nmap_interface"

class Sections():
    def __init__(self):
        self.sections = {
            "Reconnaissance": [{"Nmap": LINK_NMAP_INTERFACE}, {"Nmap": "/nmap_interface"}],
            "Weaponization": [{"Nmap": "/nmap_interface"}],
            "Delivery": [{"Nmap": "/nmap_interface"}],
            "Exploitation": [{"Nmap": "/nmap_interface"}],
            "Installation": [{"Nmap": "/nmap_interface"}],
            "Command and Control": [{"Nmap": "/nmap_interface"}],
            "Action": [{"Nmap": "/nmap_interface"}]
        }

        self.LINK_NMAP_INTERFACE = '/nmap_interface'
        self.LINK_NMAP_RESULTS = '/nmap_results'
        self.LINK_NMAP_SAVE_RESULTS = '/nmap_save_results'