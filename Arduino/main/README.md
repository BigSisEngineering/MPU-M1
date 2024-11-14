sudo apt update
sudo apt install -y curl avrdude
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
echo 'export PATH=$PATH:$HOME/bin' >> ~/.bashrc
source ~/.bashrc
arduino-cli config init
arduino-cli core update-index
arduino-cli core install arduino:avr
cd ~/Arduino/main
arduino-cli lib install "TimerOne"
arduino-cli compile --fqbn arduino:avr:leonardo .
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:leonardo .
