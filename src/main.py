#!/usr/bin/env python3
import time
from queue import Queue
from threading import Event
from blackbox import Camera, Recorder


def main():
    exit_event = Event()
    frame_queue = Queue()
    camera = Camera(frame_queue, exit_event=exit_event)
    recorder = Recorder(frame_queue, exit_event=exit_event)

    try:
        camera.start()
        recorder.start()

        while not exit_event.is_set():
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Keyboard interrupt received. Stopping recording...")

    finally:
        exit_event.set()
        camera.stop()
        recorder.stop()
        print("All threads stopped. Exiting.")

        # cleanup
        frame_queue.queue.clear()
        print("Exiting program.")


if __name__ == "__main__":
    main()
