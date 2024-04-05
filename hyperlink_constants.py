LINK_NMAP_INTERFACE = "/nmap"
LINK_NMAP_RESULTS = "/nmap_results"
LINK_NMAP_SAVE_RESULTS = "/nmap_save_results"
LINK_THE_HARVESTER_INTERFACE = "/theHarvester"
LINK_THE_HARVESTER_RESULTS = "/theHarvester_results"
LINK_THE_HARVESTER_SAVE_RESULTS = "/theHarvester_save_results"

SECTIONS = {
    "Reconnaissance": [
        {"Nmap": LINK_NMAP_INTERFACE},
        {"theHarvester": LINK_THE_HARVESTER_INTERFACE},
    ],
    "Weaponization": [{"Nmap": "/nmap_interface"}],
    "Delivery": [{"Nmap": "/nmap_interface"}],
    "Exploitation": [{"Nmap": "/nmap_interface"}],
    "Installation": [{"Nmap": "/nmap_interface"}],
    "Command and Control": [{"Nmap": "/nmap_interface"}],
    "Action": [{"Nmap": "/nmap_interface"}],
}
