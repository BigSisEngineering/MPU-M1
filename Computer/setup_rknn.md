```
Install  Win32DiskImager Software from https://win32diskimager.org/ to write OS image to eMMC module through eMMC reader.

you can follow the guide provided in this link https://docs.radxa.com/en/rock5/rock5a/getting-started/install-os?target=emmc-module

Official OS for Rock5A can be downloaded from https://docs.radxa.com/en/rock5/official-images
```

```
$ sudo apt-get update
$ sudo apt-get install python3-dev gcc
```

source: https://github.com/thanhtantran/rknn-multi-threaded-3588

```
$ scp C:\Users\Tan\Documents\Github\M3_Season2024\ComputerVision\rknn_setup_files\rknn_toolkit_lite2-1.5.2-cp39-cp39-linux_aarch64.whl rock@m3-1-g12:/tmp/.
```

```
$ python3 -m pip install /tmp/rknn_toolkit_lite2-1.5.2-cp39-cp39-linux_aarch64.whl
```

```
$ scp C:\Users\Tan\Documents\Github\M3_Season2024\ComputerVision\rknn_setup_files\librknnrt.so rock@m3-1-g12:/tmp/.
```

```
$ sudo mv /tmp/librknnrt.so /usr/lib
```
