import sys
import threading
import queue
import time

#declaring input variables
input_list = sys.argv
slider = int(input_list[1])
thread_number = int(input_list[2])
block_lenght = int(input_list[3])

#creating input queue and output queue locks
inputQueueLock = threading.Lock()
outputQueueLock = threading.Lock()

#forming the new alphabet dictionary
alphabet = "abcdefghijklmnopqrstuvwxyz"
key = alphabet[slider:] + alphabet[:slider]
key_dict = {}
for i in range(0, len(alphabet)):
    key_dict[alphabet[i]] = key[i].upper()

#overwriting thread
class myThread (threading.Thread):
    def __init__(self, threadID, name, inputQ, outputQ):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.inputQ = inputQ
        self.outputQ = outputQ
    
    def run(self):
        print("Starting" + self.name)
        encrypt_data(self.name, self.inputQ, self.outputQ)
        print("Exiting" + self.name)

#defining encryption function      
def encrypt_data(threadName, inputQ, outputQ):
    while True:
        inputQueueLock.acquire()
        if not inputQ.empty():
            line = inputQ.get()
            if line == "Quiting Thread":
                print("%s received quit request" % (threadName))
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
            
#opening files
#text = open(r"C:\Users\alika\Desktop\Dağıtık sistemler 2020\dagitik2020\odev04\input.txt", "r")
text = open("input.txt", "r")
#encrypted_text = open(r"C:\Users\alika\Desktop\Dağıtık sistemler 2020\dagitik2020\odev04\crypted_thread_11_6_40.txt", "w")
encrypted_text = open("crypted_thread_11_6_40.txt", "w")
#forming data queues
text_queue = queue.Queue()
encrypted_text_queue = queue.Queue()


#Declaring variables for threads
threads = []
threadID = 1
threadName = 1
threadList_names = []

#creating new threads
for i in range(0, thread_number):
    name = "Thread" + " " + str(threadName)
    threadList_names.append(name)
    threadName += 1

for tname in threadList_names:
    thread = myThread(threadID, tname, text_queue, encrypted_text_queue)
    thread.start()
    threads.append(thread)
    threadID += 1

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

#notifying threads for exiting
for tname in threadList_names:
    text_queue.put("Quiting Thread")

#waiting for all threads to complete
for t in threads:
    t.join()

#writing output queue to file
while not encrypted_text_queue.empty():
    string = encrypted_text_queue.get()
    encrypted_text.write(string)

#closing files
text.close()
encrypted_text.close()

print("Exiting Main Thread")
    