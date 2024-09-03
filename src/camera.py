import cv2
import time

DURATION = 5


def init_camera():
    try:
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Failed to open the camera.")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)

        ret, _ = cap.read()
        if not ret:
            print("Failed to capture an image")
            cap.release()
            return None

        return cap

    except Exception as e:
        print("An error occurred while initializing the camera.")
        return None


def capture_video(cap, duration=DURATION, fps=30, display=True):
    frames = []
    start_time = time.time()
    frame_time = 1 / fps

    while True:
        loop_start = time.time()
        ret, frame = cap.read()

        if not ret:
            print("Failed to capture frame.")
            break

        if display:
            cv2.imshow("Recording", frame)

        frames.append(frame)

        # 현재 시간에서 시작 시간을 뺀 시간이 지정한 duration보다 커지면 loop를 빠져나간다.
        elapsed_time = time.time() - start_time
        if elapsed_time > duration:
            break

        # frame rate를 컨트롤한다. 걸리는 시간과 상관없이 동일한 프레임을 캡쳐하도록 한다.
        time_to_sleep = frame_time - (time.time() - loop_start)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)

        print(f"Recording: {elapsed_time:.2f}/{duration} seconds", end="\r")

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    print("\nRecording complete.")
    cv2.destroyAllWindows()
    return frames
