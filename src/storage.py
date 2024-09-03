from datetime import datetime
import os
import cv2
import shutil

from logger import logger


def generate_filename():
    now = datetime.now()
    filename = now.strftime("%Y%m%d_%H%M%S")
    foldername = now.strftime("%Y%m%d_%H")

    return filename, foldername


def create_storage_path(base_path):
    filename, foldername = generate_filename()
    full_path = os.path.join(base_path, foldername)
    os.makedirs(full_path, exist_ok=True)

    return os.path.join(full_path, filename)


def save_video(frames, filename, fps=30):
    global total_storage_size

    if not frames:
        logger.warn("No frames to save")
        return False

    filename = f"{filename}.avi"
    height, width = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

    try:
        for frame in frames:
            out.write(frame)
    except Exception as e:
        logger.error(f"Error while writing video: {str(e)}")
        return False
    finally:
        out.release()

    file_size = os.path.getsize(filename)
    total_storage_size += file_size

    logger.info(f"Video saved successfully: {filename}")
    return True


def get_directory_size(path):
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def init_storage_size(base_path):
    global total_storage_size
    total_storage_size = get_directory_size(base_path)


def manage_storage(base_path, max_size_gb=3):
    global total_storage_size
    max_size_bytes = max_size_gb * 1024 * 1024 * 1024

    while total_storage_size > max_size_bytes:
        folders = sorted(
            [
                f
                for f in os.listdir(base_path)
                if os.path.isdir(os.path.join(base_path, f))
            ],
            key=lambda x: datetime.strptime(x, "%Y%m%d_%H"),
        )

        if not folders:
            break

        oldest_folder = os.path.join(base_path, folders[0])
        folder_size = get_directory_size(oldest_folder)
        logger.info(f"Deleting oldest folder: {oldest_folder}")

        try:
            shutil.rmtree(oldest_folder)
            total_storage_size -= folder_size
        except Exception as e:
            logger.error(f"Error deleting folder {oldest_folder}: {str(e)}")
            break

    logger.info(
        f"Storage management complete. Current size: {get_directory_size(base_path) / (1024*1024*1024):.2f} GB"
    )
