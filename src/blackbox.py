import os
import cv2
import time
from datetime import datetime
from threading import Thread, Event

from utils import create_folder, manage_storage

# 설정에 필요한 상수
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS = 30
DURATION = 60
BASE_FOLDER = "recordings"
MAX_STORAGE_GB = 0.5


class Camera:
    def __init__(self, frame_queue, exit_event, fps=FPS):
        """
        카메라를 초기화한다.
        - frame_queue: 캡쳐된 프레임을 저장할 큐 (멀티쓰레드에서 자원을 안전하게 공유하기위해 큐를 사용한다.)
        - exit_event: 카메라 종료가 필요할때 사용한 커스텀 이벤트 (쓰레드를 닫을 수 있게 커스텀 이벤트 활용)
        """
        self.frame_queue = frame_queue
        self.fps = fps
        self.exit_event = exit_event
        self.thread = None

    def start(self):
        """카메라 캡쳐를 위한 별도의 쓰레드를 시작한다."""
        self.thread = Thread(target=self._capture_video)
        self.thread.start()
        print("Starting the camera thread.")

    def stop(self):
        """카메라 쓰레드를 종료한다."""
        print("Stopping camera thread...")
        self.exit_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def _capture_video(self):
        """
        실제 카메라 캡쳐가 이루어지고, 프레임을 컨트롤한다.

        - 종료 이벤트가 발생하기 전까지 카메라 캡쳐는 계속 실행된다.
        - 캡쳐가 실제 fps보다 많이 발생하지 않도록 컨트롤한다. (실제 fps보다 적은 경우에 대해서는 커버하지 않음)
        """
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Failed to open the camera.")
            self.exit_event.set()
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, FPS)

        next_frame_time = time.time()

        try:
            while not self.exit_event.is_set():
                current_time = time.time()

                # 현재 카메라 시간이 프레임이 찍여야 할 예정 시간보다 작아지면 너무 많은 프레임이 찍힐 수 있으므로 이를 방지하는 코드
                if current_time >= next_frame_time:
                    ret, frame = cap.read()
                    if ret:
                        self._handle_frame(frame)
                    # next_frame_time을 갱신
                    next_frame_time += 1 / self.fps
                else:
                    # 카메라 캡쳐가 순식간에 이뤄진다고 가정하고 프레임레이트 만큼 일시 정지한다.
                    time.sleep(1 / self.fps)
        finally:
            cap.release()

    def _handle_frame(self, frame):
        """
        프레임에 현재 시간을 출력하고 결과를 큐에 저장한다.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(
            img=frame,
            text=timestamp,
            org=(10, 30),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(255, 255, 255),
            thickness=2,
        )
        if not self.frame_queue.full():
            self.frame_queue.put(frame)


class Recorder:
    def __init__(
        self,
        frame_queue,
        base_folder=BASE_FOLDER,
        duration=DURATION,
        fps=FPS,
        exit_event=None,
        max_storage_GB=MAX_STORAGE_GB,
    ):
        self.frame_queue = frame_queue
        self.base_folder = base_folder
        self.duration = duration
        self.fps = fps
        self.exit_event = exit_event
        self.max_storage_GB = max_storage_GB
        self.thread = None

    def start(self):
        self.thread = Thread(target=self._record)
        self.thread.start()
        print("Starting recorder thread.")

    def stop(self):
        print("Stopping record thread...")
        self.exit_event.set()

        # thread를 정리하고 종료시킨다
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def _record(self):
        """
        큐에서 받은 프레임을 저장할 수 있도록 모은다.
        프레임이 다 모이면 _save_video를 호출해 저장한다.
        """
        while not self.exit_event.is_set():
            frames = []
            expected_frames = int(self.duration * self.fps)

            while len(frames) < expected_frames:
                if not self.frame_queue.empty():
                    frames.append(self.frame_queue.get())
                else:
                    time.sleep(1 / self.fps)

            if frames:
                self._save_video(frames)

    def _save_video(self, frames):
        """
        프레임을 비디오파일로 저장한다.
        저장 폴더가 지정된 용량을 초과한 경우 오래된 폴더부터 삭제한다.
        """
        output_folder = create_folder(self.base_folder)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_folder, f"{timestamp}.avi")

        height, width = frames[0].shape[:2]

        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(
            filename=filename,
            fourcc=fourcc,
            fps=self.fps,
            frameSize=(width, height),
        )

        for frame in frames:
            out.write(frame)

        out.release()
        print(
            f"Video saved: {filename}, Frames: {len(frames)}, Duration: {len(frames)/self.fps:.2f} seconds"
        )

        manage_storage(self.base_folder, self.max_storage_GB)
