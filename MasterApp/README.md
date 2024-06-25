## BigSis Smart Cage MasterApp

### Introduction

### Log

- [v5.1.0] - 25 June 2024
  - Data collection for Diet Dispenser

### How to use

1. Copy folder

```
$ scp -r <path to masterapp> linaro@<hostname>:~/.
```

2. Connect to remote tinker

```
$ ssh linaro@<hostname>
```

3. Run setup and follow instructions

```
$ sed -i 's/\r//' /home/linaro/MasterApp/setup.sh && chmod +x /home/linaro/MasterApp/setup.sh && /home/linaro/MasterApp/setup.sh
```
