import time
import threading
import multiprocessing
import numpy as np


def sum_range(start, end):
    return np.sum(np.arange(start, end + 1, dtype=np.int64))


def single_thread():
    start_time = time.perf_counter()
    result = np.sum(np.arange(1, 100_000_001, dtype=np.int64))
    end_time = time.perf_counter()
    print(f"단일 스레드 결과: {result}")
    print(f"실행 시간: {end_time - start_time:.4f} 초")


def multi_thread(num_threads=8):
    start_time = time.perf_counter()
    chunk_size = 100_000_000 // num_threads
    threads = []
    results = [0] * num_threads

    def thread_task(start, end, index):
        results[index] = sum_range(start, end)

    for i in range(num_threads):
        start = i * chunk_size + 1
        end = start + chunk_size - 1 if i < num_threads - 1 else 100_000_000
        thread = threading.Thread(target=thread_task, args=(start, end, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(results)
    end_time = time.perf_counter()
    print(f"멀티 스레드 결과 (스레드 {num_threads}개): {total_sum}")
    print(f"실행 시간: {end_time - start_time:.4f} 초")


def multi_process(num_processes=8):
    start_time = time.perf_counter()
    chunk_size = 100_000_000 // num_processes

    with multiprocessing.Pool(processes=num_processes) as pool:
        ranges = [
            (i * chunk_size + 1, (i + 1) * chunk_size) for i in range(num_processes)
        ]
        results = pool.starmap(sum_range, ranges)

    total_sum = sum(results)
    end_time = time.perf_counter()
    print(f"멀티 프로세스 결과 (프로세스 {num_processes}개): {total_sum}")
    print(f"실행 시간: {end_time - start_time:.4f} 초")


if __name__ == "__main__":
    print("1부터 1억까지의 합 계산")
    single_thread()
    multi_thread()
    multi_process()
