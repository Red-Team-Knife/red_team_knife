#!/bin/bash

sudo apt update
sudo apt install nmap feroxbuster theharvester git python3-pip libicu-dev python3-icu pkg-config -y

git clone https://github.com/vulnersCom/nmap-vulners.git
sudo mv nmap-vulners /usr/share/nmap/scripts/nmap-vulners

pip install loguru

mkdir tools
cd tools

git clone https://github.com/mikechabot/smtp-email-spoofer-py.git
cd smtp-email-spoofer-py
pip install -r requirements.txt

cd ..
git clone https://github.com/w4af/w4af.git
cd w4af
python -m pip install --upgrade pipenv wheel
pipenv install
npm install

echo "Setup completed."
