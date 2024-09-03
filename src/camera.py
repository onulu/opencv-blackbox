import cv2
import time
from datetime import datetime

from logger import logger

from config import DURATION


def init_camera():
    try:
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            logger.error("Failed to open the camera.")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)

        ret, _ = cap.read()
        if not ret:
            logger.error("Failed to capture an image")
            cap.release()
            return None

        return cap

    except Exception as e:
        logger.error("An error occurred while initializing the camera.")
        return None


def capture_video(cap, duration=DURATION, fps=30, display=True):
    frames = []
    start_time = time.time()
    frame_time = 1 / fps

    while True:
        ret, frame = cap.read()

        if not ret:
            logger.error("Failed to capture frame.")
            break

        if display:
            cv2.imshow("Recording", frame)

        frames.append(frame)

        # 현재 시간에서 시작 시간을 뺀 시간이 지정한 duration보다 커지면 loop를 빠져나간다.
        elapsed_time = time.time() - start_time
        if elapsed_time >= duration:
            break

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(
            frame,
            current_time,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        time_to_next_frame = start_time + len(frames) * frame_time - time.time()
        if time_to_next_frame > 0:
            time.sleep(time_to_next_frame)

        logger.info(f"Recording: {elapsed_time:.2f}/{duration} seconds")

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    actual_fps = len(frames) / elapsed_time
    logger.info(
        f"Captured {len(frames)} frames in {elapsed_time:.2f} seconds (FPS: {actual_fps:.2f})"
    )

    cv2.destroyAllWindows()
    return frames
