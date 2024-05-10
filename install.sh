#!/bin/bash
sudo su

# Install nmap
sudo apt update
sudo apt install nmap -y

# Install Feroxbuster
sudo apt install feroxbuster -y

# Install theHarvester
sudo apt install theharvester -y

# Install nmap-vulners script
git clone https://github.com/vulnersCom/nmap-vulners.git
sudo cp nmap-vulners /usr/share/nmap/scripts/nmap-vulners

# Install loguru
pip install loguru

mkdir tools
# Change directory to tools
cd tools

# Install smtp_email_spoofer
git clone https://github.com/mikechabot/smtp-email-spoofer-py.git
cd smtp-email-spoofer-py
pip install -r requirements.txt

# Install w4af
sudo apt install git python3-pip libicu-dev python3-icu pkg-config -y
git clone https://github.com/w4af/w4af.git
cd w4af
python -m pip install --upgrade pipenv wheel
pipenv install
npm install

echo "Installation completed."
