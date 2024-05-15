#!/bin/bash

# Ask for the hostname number and set the hostname
read -p "Enter the number for the hostname (n in cage1x000{n}): " n
if (( n < 10 )); then
    sudo hostnamectl set-hostname cage1x000$n
else
    sudo hostnamectl set-hostname cage1x00$n
fi

# Refresh the hostname for the current session to avoid resolution errors
sudo hostname $(hostnamectl --static)

# Update and install pip if not installed
sudo apt-get update
sudo apt-get install -y python3-pip

# Install Python packages from the existing requirements.txt
sudo pip3 install -r ./requirements.txt

# Make sure check_date.sh is executable
sudo chmod +x ./check_date.sh

# Place the existing webapp.service in the correct directory and set it up
sudo cp ./webapp.service /etc/systemd/system/webapp.service
sudo systemctl daemon-reload
sudo systemctl enable webapp.service
sudo systemctl start webapp.service

echo "Setup complete."
