#!/bin/bash
# Define color variables
success='\033[0;32m'
warning='\033[0;33m'
error='\033[0;31m'
nc='\033[0m'

# ======================================= Title ====================================== #
echo -e "\n=================================================\n"
echo -e "${success}              SETUP MODULE-1 CAGE                ${nc}"
echo -e "\n=================================================\n"

# =============================== Enable Chrony Service ============================== #
sudo apt install chrony -y
sudo systemctl start chrony
sudo systemctl enable chrony

# ==================================== User Input ==================================== #
echo -e "\n=================================================\n"
read -p "Enter row number (r in cage{r}x000{n}): " r
read -p "Enter cage number (n in cage{r}x000{n}): " n
echo -e "\n=================================================\n"

# ================================== Validate Input ================================== #
if ! [[ "$r" =~ ^[0-9]+$ ]] || ! [[ "$n" =~ ^[0-9]+$ ]]; then
    echo -e "${error}[ERROR]: Both row and cage numbers must be integers.${nc}"
    exit 1
fi

# ================================== Update Hostname ================================= #
if (( n > 15 )); then
    echo -e "${error}[ERROR]: The value of n cannot exceed 15.${nc}"
    exit 1
fi

if (( n < 10 )); then
    hostname="cage${r}x000${n}"
elif (( n < 100 )); then
    hostname="cage${r}x00${n}"
elif (( n < 1000 )); then
    hostname="cage${r}x0${n}"
else
    hostname="cage${r}x${n}"
fi

# # Update /etc/hostname
echo "$hostname" | sudo tee /etc/hostname > /dev/null
sudo hostname "$hostname"
echo -e "${success}[SUCESS]>> Hostname updated to '$hostname'${nc}"

# # Update /etc/hosts
sudo sed -i "/^127.0.0.1\s*localhost\s*$/a 127.0.0.1\tlocalhost $hostname" /etc/hosts
echo -e "${success}[SUCESS]>> Hostname '$hostname' appended to '/etc/hosts'${nc}"

# =================================== System Update ================================== #
sudo apt-get update
sudo apt-get install libnss-mdns -y
sudo apt-get install -y python3-pip

# install requirements
pip3 install --upgrade pip --user
pip3 install --upgrade pip setuptools wheel --user
pip3 install -r ~/Computer/requirements.txt --user

# ================================== Setup services ================================== #
sudo cp ~/Computer/webapp.service /etc/systemd/system/webapp.service
sudo systemctl daemon-reload
sudo systemctl enable webapp.service

# ========================== End ========================= #
echo -e "\n=================================================\n"
echo -e "${success}System will reboot in 10 seconds.${nc}\nYou can access the cage webpage at $hostname:8080 after the reboot.\n"
echo -e "\n=================================================\n"
sleep 10
sudo reboot