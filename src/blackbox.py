from logger import logger
from camera import init_camera, capture_video
from storage import create_storage_path, save_video, manage_storage, init_storage_size
from config import BASE_PATH, FPS, DURATION, MAX_STORAGE_GB


class BlackBox:
    def __init__(self):
        self.cap = init_camera()
        if self.cap is None:
            logger.error("Failed to initialize camera.")
            raise RuntimeError("Camera initialization failed")
        init_storage_size(BASE_PATH)

        # self.frame_queue = queue.Queue(maxsize=FPS )
        # self.video_queue = queue.Queue(maxsize=5)

    def run(self):
        try:
            while True:
                frames = capture_video(
                    self.cap, duration=DURATION, fps=FPS, display=False
                )
                if not frames:
                    break

                full_path = create_storage_path(BASE_PATH)

                if save_video(frames, full_path):
                    logger.info(f"Video saved: {full_path}")
                else:
                    logger.error("Failed to save video.")

                manage_storage(BASE_PATH, MAX_STORAGE_GB)
        except Exception as e:
            logger.exception(f"An error occurred: {str(e)}")
        finally:
            self.cap.release()
