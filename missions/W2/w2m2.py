from multiprocessing import Process



def print_continent(name="Asia"):
    print(f"The name of continent is : {name}")


if __name__ == "__main__":
    continents = ["America","Europe","Africa"]
    processes = []

    default_process = Process(target=print_continent)
    processes.append(default_process)

    for cont in continents:
        p = Process(target=print_continent, args=(cont,))
        processes.append(p)

    for p in processes:
        p.start()
    
    for p in processes:
        p.join()
        