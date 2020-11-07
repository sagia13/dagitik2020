import sys
from multiprocessing import Lock, Process, Queue, current_process, Manager
import queue
import time

def main():
    #defining encryption function  
    def encrypt_data(inputQ, outputQ):
        while True:
            inputQueueLock.acquire()
            if not inputQ.empty():
                line = inputQ.get()
                if line == "Quiting Process":
                    print("%s received quit request" % (current_process().name))
                    inputQueueLock.release()
                    break
                line = line.lower()
                encrypted_line = ""
                for letter in line:
                    if letter in key_dict.keys():
                        encrypted_line = encrypted_line + key_dict[letter]
                    else:
                        encrypted_line = encrypted_line + letter
                inputQueueLock.release()
                outputQueueLock.acquire()
                outputQ.put(encrypted_line)
                outputQueueLock.release()
            else:
                inputQueueLock.release()
                time.sleep(1)

    #declaring input variables
    input_list = sys.argv
    slider = int(input_list[1])
    process_number = int(input_list[2])
    block_lenght = int(input_list[3])

    #creating input queue and output queue locks
    inputQueueLock = Lock()
    outputQueueLock = Lock()

    #forming the new alphabet dictionary
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    key = alphabet[slider:] + alphabet[:slider]
    key_dict = {}
    for i in range(0, len(alphabet)):
        key_dict[alphabet[i]] = key[i].upper()


    #opening files
    text = open("input.txt","r")
    encrypted_text = open("crypted_fork_14_6_48.txt", "w")

    #forming data queues
    m = Manager()
    text_queue = m.Queue()
    encrypted_text_queue = m.Queue()

    #forming process list
    processes = []

    #Creating new processes
    for i in range(0, process_number):
        p = Process(target=encrypt_data, args=(text_queue, encrypted_text_queue))
        p.start()
        processes.append(p)

    #filling the input queue
    total_elements_in_queue = 0
    inputQueueLock.acquire()
    while True:
        char = text.read(block_lenght)
        if not char:
            break
        text_queue.put(char)
        total_elements_in_queue += 1
    inputQueueLock.release()

    #waiting for input queue to be empty
    while not text_queue.empty():
        pass

    #waiting for output queue to be full
    while encrypted_text_queue.qsize() != total_elements_in_queue:
        pass

    #notifying processes for exiting
    for i in range(0, process_number):
        text_queue.put("Quiting Process")

    #waiting processes for exiting
    for p in processes:
        p.join()

    #writing output queue to file
    while not encrypted_text_queue.empty():
        string = encrypted_text_queue.get()
        encrypted_text.write(string)

    #closing files
    text.close()
    encrypted_text.close()

    print("Exiting Main Process")

if __name__ == '__main__':
    main()