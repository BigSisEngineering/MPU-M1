## BigSis Smart Cage system

### Introduction

### Log

- [v4.10.4] - 31 Jan 2024
  - Added a time delay to simulate the AI useage
- [v4.10.3] - 31 Jan 2024
  - Modify the parallel action of the system
  - Implement the interval timer check for the dummy
  - Check the `test_dummy()` and `test_pnp()` in [operation](src/operation/__init__.py)
- [v4.10.1] - 26 Jan 2024
  - v4.10.0 created parallel AI with actuation
  - this version fixed the AWS image backup blur
  - Ensure the cycle time in range of 3.75s - 4.2s
- [v4.9.1] - 24 Jan 2024
  - Fixed the timeout duration for pot in PnP
- [v4.9.0] - 23 Jan 2024
  - The images are saved in the RAM
  - Support AWS image upload in real-time
- [v4.8.1] - 22 Jan 2024
  - Fixed the AI input image resolution
- [v4.8.0] - 22 Jan 2024
  - Added pot duration timer, Fixed #6.
  - The photo name will be reflect the system action
  - if the pot is unloaded by timer, the `CONFIDENCE` and `RESULT` will be `0`
    `[CAGE_ID]_[DATE][TIME]_0_0.jpg`
- [v4.7.0] - 22 Jan 2024
  - Fixed the image naming method
    `[CAGE_ID]_[DATE][TIME]_[CONFIDENCE]_[RESULT].jpg`
- [v4.6.0] - 19 Jan 2024
  - Added AI for PnP
  - Removed data streaming and capture of dummy
  - AI time is 0.8 - 1.2s
- [v4.5.0] - 18 Jan 2024
  - Clean up the execute thread, ensure operating cycle is 3.6s
- [v4.4.0] - 17 Jan 2024
  - Upgraded the image quality
- [v5.0.0] - 28 May 2024
  - Removed streamlit. Implemented cycle time for PNP.
  - javascript for the frontend
  - implemented find circle algorithm
  - added 20 sec logic for monfoDB to initialize new session when sensors (buffer and loader) are not triggered for 20 sec
- [v5.0.1] - 30 May 2024
  - Reworked setup.sh
  - Fixed time sync bug
- [v5.0.2] - 17 June 2024
  - Display camera error
  - PNP will not execute if camera is faulty
- [v5.0.3] - 19 June 2024
  - Now prevent PNP or DUMMY to start if servos not init
- [v5.0.4] - 20 June 2024
  - Init servos at the boot and attempt to re-init if servos errors (max = 3)
- [v5.0.5] - 24 June 2024
  - Init servos at the boot and attempt to re-init if servos errors (max = 3) -- bug fix

### How to use

1. Copy folder

```
$ scp -r <path to computer> linaro@<hostname>:~/.
```

2. Connect to remote tinker

```
$ ssh linaro@<hostname>
```

3. Run setup and follow instructions

```
$ sed -i 's/\r//' /home/linaro/Computer/setup.sh && chmod +x ~/Computer/setup.sh && ~/Computer/setup.sh
```

### TODO

[] Increase the threshold of the star wheel overload
