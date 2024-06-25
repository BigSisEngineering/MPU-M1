import requests
import os
import threading

# ------------------------------------------------------------------------------------------------ #
from src import setup, comm
from src import CLI
from src.CLI import Level


def aws_image_upload(predict, img_name):
    url = "http://18.135.115.43/api/api/postgres_apis/upload_image_path/"
    payload = {"path_name": f"bigsis-m1/{setup.ROW_NUMBER}/{setup.CAGE_ID}/{predict}/"}
    print(f'aws-image-upload {predict}')
    files = [("image", (img_name, open(img_name, "rb"), "image/jpg"))]
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    return response


def create_thread():
    global KILLER
    folder_path = "/dev/shm"

    @comm.timing_decorator(interval_s=5)
    def upload():
        files = os.listdir(folder_path)
        jpg_files = [file for file in files if file.lower().endswith(".jpg")]
        CLI.printline(Level.DEBUG, f"(aws)-number of photos - {len(jpg_files)}.")
        if jpg_files:
            for jpg_file in jpg_files:
                file_path = os.path.join("/dev/shm", jpg_file)
                response = aws_image_upload("egg", f"{file_path}")
                if response.status_code >= 200 and response.status_code < 300:
                    CLI.printline(Level.INFO, f"(aws)-Uploaded: {file_path}  -- with response {response}")
                    # os.remove(file_path)
                else:
                    CLI.printline(Level.WARNING, f"(aws) internet access fail")

    def loop(killer: threading.Event):
        while not killer.is_set():
            upload()
        CLI.printline(Level.ERROR, "(aws)-thread terminated.")

    bg_thread = threading.Thread(target=loop, args=(KILLER,))
    return bg_thread


KILLER = threading.Event()
