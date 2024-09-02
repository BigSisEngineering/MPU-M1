import paramiko
from paramiko import SSHClient
from scp import SCPClient
import time
import os
import threading
import requests

row = 2

# ======================================= List of hostnames ====================================== #
hostnames = []
# for n in range(1, 14 + 1):
#     hostnames.append(f"cage{row}x00{n:02}")

for row in range(2,5):
    for n in range(1, 15):
        hostnames.append(f"cage{row}x00{n:02}")
# hostnames.append("cage2x0001")
# hostnames.append("cage3x0004")
# hostnames.append("cagetest")


# ========================== Common remote directory path for all hosts ========================== #
remote_dir = "~/."

# ==================================== Files need to transfer =================================== #
local_files = [
    "C:/Users/MarcoZacaria/Documents/Github/MPU-M1/Computer",
    # 'C:/Users/MarcoZacaria/Documents/GitHub/MPU-M1/Computer/src/data/__init__.py',
    # 'C:/Users/MarcoZacaria/Documents/GitHub/MPU-M1/Computer/src/tasks/httpServer/httpPostHandler.py'
]

data_path = "~/Computer/Statistics.log"
img_path = "~/Computer/src/tasks/camera/."

# SSH credentials
if row > 1:
    username = "rock"
    password = "rock"
else:
    username = "linaro"
    password = "linaro"

def get_data(local_path, remote_path, hostname, username, password, port=22):
    try:
        # path = f"{local_path}/{hostname[len(hostname)-2:]}.txt"
        path = f"{local_path}/{hostname}.log"
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


# def ssh_reboot(hostname, username, password, port=22):
#     try:
#         # Create an SSH client instance
#         ssh = paramiko.SSHClient()
#         ssh.load_system_host_keys()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#         # Connect to the server
#         ssh.connect(hostname, port=port, username=username, password=password, timeout=1)

#         # Execute the reboot command
#         stdin, stdout, stderr = ssh.exec_command("sudo reboot")

#         # You can capture the output or error if needed
#         # output = stdout.read()
#         # error = stderr.read()

#         print(f"Rebooted -> {hostname}")
#     except Exception as e:
#         print(f"An error occurred {hostname}: {e}")
#     finally:
#         # Close the connection
#         ssh.close()

def ssh_reboot(hostname, username, password, port=22):
    try:
        # Create an SSH client instance
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the server
        ssh.connect(hostname, port=port, username=username, password=password, timeout=1)

        # Execute the reboot command using sudo -S
        stdin, stdout, stderr = ssh.exec_command(f"echo {password} | sudo -S reboot now")

        # Capture the output or error if needed
        output = stdout.read()
        error = stderr.read()
        print(output.decode())
        print(error.decode())

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



def execute_command(hostname, command, username, password, port=22):
    try:
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port=port, username=username, password=password, timeout=60)

        stdin, stdout, stderr = ssh.exec_command(command)
        print(f"Command executed -> {hostname}: {command}")

    except Exception as e:
        print(f"Error executing command on {hostname}: {e}")

    finally:
        ssh.close()


def save_mask_requests():
    """
    This function sends a POST request to each endpoint generated by 
    varying the values of 'r' from 1 to 4 and 'n' from 01 to 14.
    """
    # Define the base URL with placeholders for r and n
    url_template = "http://cage{}x00{}:8080/SAVE_MASK"

    # Loop over the range of r and n values
    for r in range(1, 5):
        for n in range(1, 15):
            # Format n to be two digits (e.g., 01, 02, etc.)
            n_formatted = f"{n:02d}"
            
            # Format the URL with the current values of r and n
            url = url_template.format(r, n_formatted)
            
            # Send the POST request
            response = requests.post(url)
            
            # Print the status of each request
            print(f"POST to {url} - Status Code: {response.status_code}")
            time.sleep(0.5)




def restart_service(hostname):
    global username, password
    command = "sudo systemctl restart webapp.service"
    threading.Thread(target=execute_command, args=(hostname, command, username, password)).start()





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


def get_log_file(hostname):
    global username, password
    log_remote_path = f"~/Computer/{hostname}.log"
    local_log_dir = "./logs"
    if not os.path.exists(local_log_dir):
        os.makedirs(local_log_dir)
    threading.Thread(
        target=get_data,
        args=(
            local_log_dir,
            log_remote_path,
            hostname,
            username,

            password,
        ),
    ).start()


for hostname in hostnames:
    try:
        # upload_files(hostname)
        reboot(hostname)
        # remove(hostname)
        # get_logging_data(hostname)
        # get_cage_photos(hostname)
        # restart_service(hostname)
        # get_log_file(hostname)
        # save_mask_requests()
        # time.sleep(0.1)

    except Exception as e:
        print(f"Error -> {hostname} -> {e}")

# sudo scp SmartCage_4/webapp.service /etc/systemd/system/. && sudo systemctl daemon-reload && sudo systemctl restart webapp.service
