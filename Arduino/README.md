### Uploading Code to Arduino via Arduino CLI from Controller Board (Tinker/Rock/RaspberryPi)

To upload code to an Arduino board such as the Leonardo, you can use the Arduino CLI. Follow these steps on a Linux-based system:

1. **Transfer Arduino Code to the Controller Board**:
   Use SCP to transfer your Arduino project directory to the controller board:
   ```bash
   scp -r /path/to/Arduino rock@hostname:~/

2. **Connect to the Controller Board via SSH**:
    ```bash
    ssh rock@hostname

3. **Update and Install Dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y curl avrdude
 
4. **Install the Arduino CLI:**:
    ```bash
    curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh

5. **Update the System Path:** Add the Arduino CLI to your system's PATH to access it from any terminal:
    ```bash
    echo 'export PATH=$PATH:$HOME/bin' >> ~/.bashrc
    source ~/.bashrc

6. **Initialize and Update Arduino CLI:** Install the AVR core to support Arduino boards like the Leonardo:
    ```bash
    arduino-cli config init
    arduino-cli core update-index

7. **Install AVR Core:** Install the AVR core to support Arduino boards like the Leonardo:
    ```bash
    arduino-cli core install arduino:avr

8. **Install Libraries:** Install necessary Arduino libraries:
    ```bash
    arduino-cli lib install "TimerOne"

9. **Navigate to Arduino code directory on the controller board:** 
    ```bash
    cd ~/Arduino/main

10. **Compile the Sketch:**  Compile your Arduino sketch for the Leonardo board:
    ```bash
    arduino-cli compile --fqbn arduino:avr:leonardo .

11. **Upload the Sketch:** Upload the compiled sketch from the controller board to the Arduino board:
    ```bash
    arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:leonardo .



