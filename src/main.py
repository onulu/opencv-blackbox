#!/usr/bin/env python3
import cv2
import time
from camera import init_camera, capture_video
from storage import save_video, create_storage_path, manage_storage, init_storage_size

DURATION = 5
BASE_PATH = "recordings"
MAX_STORAGE_GB = 3


def main():
    cap = init_camera()
    if cap is None:
        print("Failed to initialize camera. Exiting.")
        return

    init_storage_size(BASE_PATH)

    while True:
        manage_storage(BASE_PATH, max_size_gb=MAX_STORAGE_GB)

        start_time = time.time()
        frames = capture_video(cap, duration=DURATION)

        if not frames:
            break

        full_path = create_storage_path(BASE_PATH)

        if save_video(frames, full_path):
            print(f"Video saved: {full_path}")
        else:
            print("Failed to save video")

        elapsed_time = time.time() - start_time
        if elapsed_time < DURATION:
            time.sleep(DURATION - elapsed_time)


if __name__ == "__main__":
    main()
