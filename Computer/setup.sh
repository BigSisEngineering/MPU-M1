#!/bin/bash
read -p "Enter the number for the hostname (n in cage1x000{n}): " n
if (( n < 10 )); then
    sudo hostnamectl set-hostname cage1x000$n
else
    sudo hostnamectl set-hostname cage1x00$n
fi
sudo hostname $(hostnamectl --static)
sudo apt-get install libnss-mdns -y
sudo apt-get update
sudo apt-get install -y python3-pip
sudo pip3 install -r ./requirements.txt
sudo chmod +x ./check_date.sh
sudo cp ./webapp.service /etc/systemd/system/webapp.service
sudo systemctl daemon-reload
sudo systemctl enable webapp.service
sudo systemctl start webapp.service
echo "Setup complete."