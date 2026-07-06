import multiprocessing
import time


def work_log(work_data):
    name, duration = work_data
    print(f"Process {name} waiting {duration} seconds")
    time.sleep(duration)
    print(f"Process {name} Finished.")


if __name__ == "__main__":
    work = [('A', 5), ('B', 2), ('C', 1), ('D', 3)]
    with multiprocessing.Pool(processes=2) as pool:
        pool.map(work_log, work)
