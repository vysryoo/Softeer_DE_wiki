from multiprocessing import Queue


if __name__ == "__main__":

    items = ["red", "green", "blue", "black"]

    q = Queue()
        
    print("pushing items to queue:")
    for i in range(len(items)):
        color = items[i]
        put_index = i + 1
        q.put(color)
        print(f"item no: {put_index} {color}")


    print("popping items from queue:")
    pop_index = 0
    while not q.empty():
        item = q.get()
        print(f"item no: {pop_index} {item}")
        pop_index += 1