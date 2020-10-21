import sys

airlines = open("airlines.txt", "r")
dictionary = {}
for line in airlines:
    testlist = line.split(",")
    testlist[-1] = testlist[-1].replace("\n","")
    dictionary[testlist[0]] = testlist[1:]
    
airlines.close()
all_keys = []
for i in dictionary.keys():
    all_keys.append(i)

inp_list = sys.argv    
value = inp_list[2]
key_list = []
key = inp_list[1]
found = False
print("Searching if you can transfer miles From " + key + " to " + value + ".")

def search (dictionary, key, value):
    global found
    key_list.append(key) 
    for keys in dictionary[key]:
        if value == keys:
            found = True    
        if keys not in key_list :
            search(dictionary, keys, value)
    return found
    
if search(dictionary, key, value) == True:
    print("it is possible to transfer miles from " + key + " to " + value + " : True")
    print("One of the paths is: ", end='')
    for key in key_list:
        if key != value:
            print(key  + " -> " , end='')
        else:
            print(key)      

else:
    print("it is not possible to transfer miles from " + key + " to " + value + " : False")       
            
    
        
        


    