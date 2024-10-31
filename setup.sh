#!/bin/bash

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install nmap feroxbuster theharvester commix sqlmap wpscan git python3-pip libicu-dev libxml2 python3-icu pkg-config pipenv python3-venv npm -y

git clone https://github.com/vulnersCom/nmap-vulners.git
sudo mv nmap-vulners /usr/share/nmap/scripts/nmap-vulners


mkdir tools
cd tools

git clone https://github.com/manfredigianni/smtp-email-spoofer-py.git

git clone https://github.com/w4af/w4af.git

cd ..

python3 -m venv venv
echo "export PIPENV_IGNORE_VIRTUALENVS=1" >> ./venv/bin/activate
source venv/bin/activate

pip install -r requirements.txt
cd tools
cd smtp-email-spoofer-py
pip install -r requirements.txt
cd ..
cd w4af
python -m pip install --upgrade pipenv wheel
pipenv install
npm install

echo "Setup completed."
