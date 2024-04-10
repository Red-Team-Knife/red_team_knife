from flask import url_for



SECTIONS = {
    "Reconnaissance": [
        {"Nmap": '/nmap'},
        {"theHarvester": '/theHarvester'},
    ],
    "Weaponization": [{"Nmap": "/nmap_interface"}],
    "Delivery": [{"Nmap": "/nmap_interface"}],
    "Exploitation": [{"Nmap": "/nmap_interface"}],
    "Installation": [{"Nmap": "/nmap_interface"}],
    "Command and Control": [{"Nmap": "/nmap_interface"}],
    "Action": [{"Nmap": "/nmap_interface"}],
}
