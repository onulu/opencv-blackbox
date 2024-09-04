#!/usr/bin/env python3
import time
from queue import Queue
from threading import Event
from blackbox import Camera, Recorder


def main():
    exitEvent = Event()
    frameQueue = Queue()
    camera = Camera(frameQueue, exitEvent=exitEvent)
    recorder = Recorder(frameQueue, exitEvent=exitEvent)

    try:
        camera.start()
        recorder.start()

        while not exitEvent.is_set():
            time.sleep(1)

    except KeyboardInterrupt:
        print("Keyboard interrupt received. Stopping recording...")

    finally:
        camera.stop()
        recorder.stop()
        print("All threads stopped. Exiting.")


if __name__ == "__main__":
    main()
