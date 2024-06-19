import paramiko
from paramiko import SSHClient
from scp import SCPClient
import time
import os

row = 1

# ======================================= List of hostnames ====================================== #
hostnames = []
# for n in range(1, 14 + 1):
#     hostnames.append(f"cage{row}x00{n:02}")
hostnames.append("cage1x0002")

# ========================== Common remote directory path for all hosts ========================== #
remote_dir = "~/."

# ==================================== Files need to transfer =================================== #
local_files = [
    f"C:/Users/MarcoZacaria/Documents/Github/MPU-M1/Computer",
    # f"C:/Users/Tan/Documents/Github/MPU-M1/Computer"
]

data_path = "~/Computer/Statistics.log"
img_path = "~/Computer/src/tasks/camera/."

# SSH credentials
username = "linaro"
password = "linaro"  # You may want to use SSH keys for better security


def get_data(local_path, remote_path, hostname, username, password, port=22):
    try:
        path = f"{local_path}/{hostname[len(hostname)-2:]}.txt"
        # Create an SSH client instance
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the server
        ssh.connect(hostname, port=port, username=username, password=password, timeout=60)

        # Use SCPClient to transfer the folder
        with SCPClient(ssh.get_transport(), socket_timeout=10) as scp:
            scp.get(remote_path, f"{path}", recursive=True)
        # Close the connection
        ssh.close()
        print(f"Updated -> {hostname}-> {path}")

    except Exception as e:
        print(f"Error -> {hostname}-> {path}: {e}")


def get_photo(local_path, remote_path, hostname, username, password, port=22):
    try:
        path = f"{local_path}"
        if not os.path.exists(path):
            print("Path cant find")
            os.mkdir(path)
        # Create an SSH client instance
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the server
        ssh.connect(hostname, port=port, username=username, password=password, timeout=60)

        # Use SCPClient to transfer the folder
        with SCPClient(ssh.get_transport(), socket_timeout=10) as scp:
            scp.get(remote_path, f"{path}", recursive=True)
        # Close the connection
        ssh.close()
        print(f"Updated -> {hostname}-> {path}")

    except Exception as e:
        print(f"Error -> {hostname}-> {path}: {e}")


def scp_folder(local_path, remote_path, hostname, username, password, port=22):
    try:
        # Create an SSH client instance
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the server
        ssh.connect(hostname, port=port, username=username, password=password, timeout=60)

        # Use SCPClient to transfer the folder
        with SCPClient(ssh.get_transport(), socket_timeout=3) as scp:
            scp.put(local_path, recursive=True, remote_path=remote_path)

        # Close the connection
        ssh.close()
        print(f"Updated -> {hostname}-> {local_path}")

    except Exception as e:
        print(f"Error -> {hostname}-> {local_path}: {e}")


def ssh_reboot(hostname, username, password, port=22):
    try:
        # Create an SSH client instance
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the server
        ssh.connect(hostname, port=port, username=username, password=password, timeout=1)

        # Execute the reboot command
        stdin, stdout, stderr = ssh.exec_command("sudo reboot")

        # You can capture the output or error if needed
        # output = stdout.read()
        # error = stderr.read()

        print(f"Rebooted -> {hostname}")
    except Exception as e:
        print(f"An error occurred {hostname}: {e}")
    finally:
        # Close the connection
        ssh.close()


def ssh_remove_log(hostname, username, password, port=22):
    try:
        # Create an SSH client instance
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the server
        ssh.connect(hostname, port=port, username=username, password=password, timeout=1)

        # Execute the reboot command
        stdin, stdout, stderr = ssh.exec_command(f"rm /home/linaro/SmartCage_4/src/tasks/camera/*.jpg")
        # stdin, stdout, stderr = ssh.exec_command(f"sudo rm {data_path}")

        # You can capture the output or error if needed
        # output = stdout.read()
        # error = stderr.read()

        print(f"Removed ({data_path})-> {hostname}")
    except Exception as e:
        print(f"An error occurred {hostname}: {e}")
    finally:
        # Close the connection
        ssh.close()


# Example usage
import threading


def upload_files(hostname):
    global local_files, username, password
    for file in local_files:
        threading.Thread(
            target=scp_folder,
            args=(
                file,
                remote_dir,
                hostname,
                username,
                password,
            ),
        ).start()


def reboot(hostname):
    global username, password
    threading.Thread(
        target=ssh_reboot,
        args=(
            hostname,
            username,
            password,
        ),
    ).start()


def remove(hostname):
    global username, password
    threading.Thread(
        target=ssh_remove_log,
        args=(
            hostname,
            username,
            password,
        ),
    ).start()


def get_logging_data(hostname):
    global username, password
    threading.Thread(
        target=get_data,
        args=(
            "./data_analysis/fotos",
            data_path,
            hostname,
            username,
            password,
        ),
    ).start()


def get_cage_photos(hostname):
    global username, password
    threading.Thread(
        target=get_photo,
        args=(
            f"./data_analysis/fotos_3/{hostname}",
            img_path,
            hostname,
            username,
            password,
        ),
    ).start()


for hostname in hostnames:
    try:
        
        upload_files(hostname)
        # reboot(hostname)
        # remove(hostname)
        # get_logging_data(hostname)
        # get_cage_photos(hostname)

    except Exception as e:
        print(f"Error -> {hostname} -> {e}")

# sudo scp SmartCage_4/webapp.service /etc/systemd/system/. && sudo systemctl daemon-reload && sudo systemctl restart webapp.service
