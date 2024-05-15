# Red Team Knife
![logo](https://github.com/Davide1102/red_team_knife/assets/95478950/f9b1b654-674f-4be7-8da8-5f6f7cd7202a)
![loading](https://github.com/Davide1102/red_team_knife/assets/95478950/b6148c12-9c55-4266-92fc-244813b4f487)

## Overview
Red Team Knife serves as an interface to a range of valuable red teaming tools, including:
- [Nmap](https://github.com/nmap/nmap)
- [Nmap vulnerability scanner](https://github.com/vulnersCom/nmap-vulners.git)
- [Feroxbuster](https://github.com/epi052/feroxbuster)
- [theHarvester](https://gitlab.com/kalilinux/packages/theharvester)
- Dig
- [w4af](https://github.com/w4af/w4af)*
- [SMTP Email spoofer](https://github.com/mikechabot/smtp-email-spoofer-py)*
- [Commix](https://github.com/commixproject/commix)
- [Sqlmap](https://github.com/sqlmapproject/sqlmap)

*these are the original repositories, but ```setup.sh``` will clone a fork where we fixed some bugs or some code checks to ensure everythong works with our interface.
Links to our forks are:
- [w4af](https://github.com/manfredigianni/w4af)
- [SMTP Email spoofer](https://github.com/manfredigianni/smtp-email-spoofer-py)

## Installation
To install Red Team Knife, follow these steps:

- Clone the repository.
```
sudo su
chmod +x setup.sh
./setup.sh
```
Start the application by running ```python app.py``` and connect to ```localhost:5000``` in your web browser.
If the server continues to run after closing the terminal you can try to run ```python kill_server.py```.
