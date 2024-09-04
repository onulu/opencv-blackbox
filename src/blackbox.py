import os
import cv2
import time
from datetime import datetime
from queue import Queue
from threading import Thread, Event

from utils import createFolder, manageStorage

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS = 30
DURATION = 5
BASE_FOLDER = "recordings"
MAX_STORAGE_GB = 1


class Camera:
    def __init__(self, frameQueue, exitEvent, fps=FPS):
        self.frameQueue = frameQueue
        self.fps = FPS
        self.running = Event()
        self.exitEvent = exitEvent

    def start(self):
        self.running.set()
        self.thread = Thread(target=self._captureVideo)
        self.thread.start()
        print("Starting the camera thread.")

    def stop(self):
        self.running.clear()
        if self.thread.is_alive():
            self.thread.join()
        print("Camera thread stopped.")

    def _captureVideo(self):
        cap = cv2.VideoCapture(0)
        self.fps = cap.get(cv2.CAP_PROP_FPS)

        if not cap.isOpened():
            print("Failed to open the camera.")
            self.exitEvent.set()
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, FPS)

        nextFrameTime = time.time()

        try:
            while self.running.is_set() and not self.exitEvent.is_set():
                currentTime = time.time()

                if currentTime >= nextFrameTime:
                    ret, frame = cap.read()
                    if ret:
                        self._handleFrame(frame)
                    nextFrameTime += 1 / self.fps
                else:
                    time.sleep(1 / self.fps)
        finally:
            cap.release()

    def _handleFrame(self, frame):
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
        if not self.frameQueue.full():
            self.frameQueue.put(frame)


class Recorder:
    def __init__(
        self,
        frameQueue,
        baseFolder=BASE_FOLDER,
        duration=DURATION,
        fps=FPS,
        exitEvent=None,
        maxStorageGB=MAX_STORAGE_GB,
    ):
        self.frameQueue = frameQueue
        self.baseFolder = baseFolder
        self.duration = duration
        self.fps = fps
        self.running = Event()
        self.exitEvent = exitEvent
        self.maxStorageGB = maxStorageGB

    def start(self):
        self.running.set()
        self.thread = Thread(target=self._record)
        self.thread.start()
        print("Starting the Recorder thread.")

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
        print("Recorder thread stopped.")

    def _record(self):
        while self.running.is_set() and not self.exitEvent.is_set():
            self._recordVideo()

    def _recordVideo(self):
        frames = []
        expectedFrames = int(self.duration * self.fps)

        while (
            len(frames) < expectedFrames
            and self.running.is_set()
            and not self.exitEvent.is_set()
        ):
            if not self.frameQueue.empty():
                frames.append(self.frameQueue.get())
                print(f"Appending a new frame from the queue. {str(len(frames))}")
            else:
                time.sleep(1 / self.fps)

        if frames:
            print("Start saving...")
            self._saveVideo(frames)

    def _saveVideo(self, frames):
        outputFolder = createFolder(self.baseFolder)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(outputFolder, f"{timestamp}.avi")

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

        manageStorage(self.baseFolder, self.maxStorageGB)
