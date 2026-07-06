from multiprocessing import Queue, Process, current_process
from queue import Empty
import time

def run_task(src: Queue, dest: Queue):
    while True:

        try:
            task = src.get_nowait()
        except Empty:
            break

        print(f"Task no: {task}")
        time.sleep(0.5)
        process_name = current_process().name
        dest.put(f"Task no {task} is done by {process_name}")

if __name__ == "__main__":
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()

    for i in range(10):
        tasks_to_accomplish.put(i)

    processes = []

    for _ in range(4):
        p = Process(target=run_task, args=(tasks_to_accomplish, tasks_that_are_done))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
    
    while not tasks_that_are_done.empty():
        print(tasks_that_are_done.get())