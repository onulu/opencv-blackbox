import os
import shutil
from datetime import datetime


def create_folder(baseFolder):
    foldername = datetime.now().strftime("%Y%m%d_%H")
    folderPath = os.path.join(baseFolder, foldername)
    os.makedirs(folderPath, exist_ok=True)
    return folderPath


def get_directory_size(baseFolder):
    totalSize = sum(
        os.path.getsize(os.path.join(dirpath, file))
        for dirpath, _, files in os.walk(baseFolder)
        for file in files
    )
    return totalSize


def manage_storage(basePath, maxSizeGB):
    totalSize = get_directory_size(basePath)
    maxSizeIntoBytes = maxSizeGB * 1024 * 1024 * 1024

    while totalSize > maxSizeIntoBytes:
        folders = sorted(
            [
                folder
                for folder in os.listdir(basePath)
                if os.path.isdir(os.path.join(basePath, folder))
            ],
            key=lambda x: int(x),
        )
        if not folders:
            break

        oldestFolder = os.path.join(basePath, folders[0])
        shutil.rmtree(oldestFolder)

    print(
        f"Storage management complete.  {get_directory_size(basePath) / (1024*1024*1024):.2f} GB"
    )
