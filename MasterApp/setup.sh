#!/bin/bash
# Function to validate if input is an integer
is_integer() {
    [[ $1 =~ ^[0-9]+$ ]]
}

# Define color variables
success='\033[0;32m'
warning='\033[0;33m'
error='\033[0;31m'
nc='\033[0m'


# ========================= Title ======================== #
echo -e "\n${success}=================================================${nc}\n"
echo -e "${success}                   SETUP M1 Row Master                  ${nc}"
echo -e "\n${success}=================================================${nc}\n"


# ====================== User Input ====================== #
# Prompt user for input
echo -e "\n=================================================\n"
echo -e "${success}[USER INPUT]>> Please enter the ROW number ->${nc}" && read row_input
echo -e "\n=================================================\n"


# =================== Generate Content =================== #
# Validate input
if is_integer "$row_input"; then
    hostname="m1-$row_input-m"

    if sudo ping -c 1 -W 1 "$hostname.local" >/dev/null; then
        echo -e "${error}[ERROR]>> Master detected on network!${nc}"
        echo -e "${success}[USER INPUT]>> Override? (y/n) ->${nc}" && read override

        if [[ $override == 'y' ]]; then
            echo -e "${success}Continue setup.${nc}"
        elif [[ $override == 'n' ]]; then
            echo -e "${error}Exit setup.${nc}"
            exit 1
        fi
    fi

    # Update /etc/hostname
    echo "$hostname" | sudo tee /etc/hostname > /dev/null
    sudo hostname "$hostname"
    echo -e "${success}[SUCESS]>> Hostname updated to '$hostname'${nc}"

    # Update /etc/hosts
    sudo sed -i "/^127.0.0.1\s*localhost.*/c\127.0.0.1\tlocalhost $hostname" /etc/hosts
    echo -e "${success}[SUCESS]>> Hostname '$hostname' appended to '/etc/hosts'${nc}"

else
    echo -e "${error}[ERROR]>> ROW number must be an integer!${nc}"
    exit 1
fi

# ===================== System Update ==================== #
sudo apt-get update

#install DNS
sudo apt-get install libnss-mdns -y

#install requirements
pip3 install setuptools
pip3 install --upgrade pip setuptools
pip3 install --upgrade pip --user
pip3 install -r /home/linaro/MasterApp/requirements.txt --user

# # ==================== Setup I2C Rules =================== #
# sudo sed -i 's/^#intf:i2c7=off/intf:i2c7=on/' /boot/config.txt
# sudo usermod -aG i2c linaro

# # Reload udev rules and trigger
# echo -e "${success}[SUCESS]>> Configured I2C acess${nc}"

# # # ==================== Setup GPIO Rules ================== #
# RULES_FILE="/etc/udev/rules.d/50-gpio.rules"

# # Create or overwrite the udev rules file
# cat <<EOF | sudo tee "$RULES_FILE" >/dev/null
# SUBSYSTEM=="gpio*", ACTION=="add", PROGRAM="/bin/sh -c '\
#     echo udev rule executed >> /tmp/udev.log;\
#     chown -R root:gpiouser /sys/class/gpio && chmod -R 770 /sys/class/gpio;\
#     chown -R root:gpiouser /sys/devices/virtual/gpio && chmod -R 770 /sys/devices/virtual/gpio;\
#     chown -R root:gpiouser /sys\$devpath && chmod -R 770 /sys\$devpath\
# '"
# EOF

# # Set appropriate permissions on the file
# sudo chmod 644 "$RULES_FILE"
# sudo chown root:root "$RULES_FILE"

# # Inform user about completion
# echo -e "${success}[SUCESS]>> The udev rule has been successfully installed at $RULES_FILE.${nc}"

# sudo groupadd gpiouser && sudo adduser "linaro" gpiouser
# sudo usermod -aG gpiouser linaro
# sudo udevadm control --reload-rules && sudo udevadm trigger
# echo -e "${success}[SUCESS]>> Configured GPIO access${nc}"

# ==================== Setup UART =================== #
sudo sed -i 's/^#intf:uart4=off/intf:uart4=on/' /boot/config.txt
echo -e "${success}[SUCESS]>> Configured UART access${nc}"

# ==================== Setup Autoboot ==================== #
sudo cp /home/linaro/Loader/webapp.service  /etc/systemd/system/. && sudo systemctl daemon-reload && systemctl enable webapp.service
echo -e "${success}[SUCESS]>> Created Service${nc}"


# ========================== End ========================= #
echo -e "\n=================================================\n"
echo -e "${success}System will reboot in 10 seconds.${nc}\nYou can access the webpage at $hostname:8080 after the reboot.\n"
echo -e "\n=================================================\n"
sleep 10
sudo reboot
