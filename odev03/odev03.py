from matplotlib import pyplot as plt
import numpy as np

data = open("C:\\Users\\alika\\Desktop\\Dağıtık sistemler 2020\\dagitik2020\\odev03\\data\\lab8_0.30-8.08-1.52.mbd")
datalist = []
sensor_macs = []
transmittor_macs = []

for line in data:
    new_data = line.split(",")
    if new_data[1] not in sensor_macs:
        sensor_macs.append(new_data[1])
    if new_data[2] not in transmittor_macs:
        transmittor_macs.append(new_data[2])
    datalist.append(new_data)

data.close()

sensor_macs = tuple(sensor_macs)
transmittor_macs = tuple(transmittor_macs)
sensor_transmittor_couples = {}

for sensor in sensor_macs:
    for transmittor in transmittor_macs:
        key = sensor + ":" + transmittor
        sensor_transmittor_couples[key] = []
        for data in datalist:
            if data[1] == sensor and data[2] == transmittor:
                numeric_data = int(data[3].replace("\n",""))
                sensor_transmittor_couples[key].append(numeric_data)

rssi_distribution = []
for key in sensor_transmittor_couples.keys():
    
    max_value = max(sensor_transmittor_couples[key])      
    min_value = min(sensor_transmittor_couples[key])  
    value_list = []
    for i in range(min_value,max_value+1,1):
        value_list.append(i)
    count_list = [0] * len(value_list)
    
    for value in sensor_transmittor_couples[key]:
        index = value_list.index(value)
        count_list[index] = count_list[index] + 1
    
    templist = []
    templist.append(value_list)
    templist.append(count_list)
    templist.append(key)
    rssi_distribution.append(templist)

plt.style.use("fivethirtyeight")
fig,a = plt.subplots(2,4)
a[0][0].bar(rssi_distribution[0][0], rssi_distribution[0][1], color = "#444444")
a[0][0].set_title(rssi_distribution[0][2], fontsize = "9")
a[0][1].bar(rssi_distribution[1][0], rssi_distribution[1][1], color = "#444444")
a[0][1].set_title(rssi_distribution[1][2], fontsize = "9")
a[0][2].bar(rssi_distribution[2][0], rssi_distribution[2][1], color = "#444444")
a[0][2].set_title(rssi_distribution[2][2], fontsize = "9")
a[0][3].bar(rssi_distribution[3][0], rssi_distribution[3][1], color = "#444444")
a[0][3].set_title(rssi_distribution[3][2],fontsize = "9")
a[1][0].bar(rssi_distribution[4][0], rssi_distribution[4][1], color = "#444444")
a[1][0].set_title(rssi_distribution[4][2],fontsize = "9")
a[1][1].bar(rssi_distribution[5][0], rssi_distribution[5][1], color = "#444444")
a[1][1].set_title(rssi_distribution[5][2],fontsize = "9")
a[1][2].bar(rssi_distribution[6][0], rssi_distribution[6][1], color = "#444444")
a[1][2].set_title(rssi_distribution[6][2],fontsize = "9")
a[1][3].bar(rssi_distribution[7][0], rssi_distribution[7][1], color = "#444444")
a[1][3].set_title(rssi_distribution[7][2],fontsize = "9")
fig.suptitle("RSSI Distributions")
fig.set_figheight(6)
fig.set_figwidth(12)
plt.show()
   
freq_time = {}
    
for sensor in sensor_macs:
    for transmittor in transmittor_macs:
        key = sensor + ":" + transmittor
        freq_time[key] = []
        freq_time[key].append([])
        freq_time[key].append([])
        w = 0
        flag = False
        for data in datalist:        
            if data[1] == sensor and data[2] == transmittor:
                if not flag:
                    freq_time[key][0].append(float(data[0]))
                    w = w  + 1
                    if w == 100:
                        flag = True
                        t = freq_time[key][0][-1]
                        tw = freq_time[key][0][0]
                        frequency = 100 / (t - tw)
                        freq_time[key][1].append(frequency)
                else:
                    freq_time[key][0] = freq_time[key][0][1:]
                    freq_time[key][0].append(float(data[0]))
                    t = freq_time[key][0][-1]
                    tw = freq_time[key][0][0]
                    frequency = 100 / (t - tw)
                    freq_time[key][1].append(frequency)

frequencylist = []
keylist = []
range_list = []
for i in np.arange(1.5, 2.5, 0.05):
    range_list.append(float(i))

range_list = range_list[1:]

key_frequency_couple = []

for i in freq_time.keys():
    keylist.append(i)
    frequencylist.append(freq_time[i][1])

    count_list = [0]* len(range_list)
    for frequency in freq_time[i][1]:
        counter = 1
        while counter < (len(range_list) - 1):
            if frequency < range_list[counter]:
                count_list[counter] = count_list[counter] + 1
                break
            else:
                counter = counter + 1
    templist = []
    templist.append(i)
    templist.append(range_list)
    templist.append(count_list)
    key_frequency_couple.append(templist)
    

plt.style.use("fivethirtyeight")
fig,a = plt.subplots(2,4)
a[0][0].plot(frequencylist[0], color = "#444444")
a[0][0].set_title(keylist[0], fontsize = "9")
a[0][1].plot(frequencylist[1], color = "#444444")
a[0][1].set_title(keylist[1], fontsize = "9")
a[0][2].plot(frequencylist[2], color = "#444444")
a[0][2].set_title(keylist[2], fontsize = "9")
a[0][3].plot(frequencylist[3], color = "#444444")
a[0][3].set_title(keylist[3], fontsize = "9")
a[1][0].plot(frequencylist[4], color = "#444444")
a[1][0].set_title(keylist[4], fontsize = "9")
a[1][1].plot(frequencylist[5], color = "#444444")
a[1][1].set_title(keylist[5], fontsize = "9")
a[1][2].plot(frequencylist[6], color = "#444444")
a[1][2].set_title(keylist[6], fontsize = "9")
a[1][3].plot(frequencylist[7], color = "#444444")
a[1][3].set_title(keylist[7], fontsize = "9")
fig.suptitle("Anlık frekans değişimleri")
fig.set_figheight(6)
fig.set_figwidth(12)
plt.show()



plt.style.use("fivethirtyeight")
fig,a = plt.subplots(2,4)
a[0][0].bar(key_frequency_couple[0][1], key_frequency_couple[0][2], color = "#444444")
a[0][0].set_title(key_frequency_couple[0][0], fontsize = "9")
a[0][1].bar(key_frequency_couple[1][1], key_frequency_couple[1][2], color = "#444444")
a[0][1].set_title(key_frequency_couple[1][0], fontsize = "9")
a[0][2].bar(key_frequency_couple[2][1], key_frequency_couple[2][2], color = "#444444")
a[0][2].set_title(key_frequency_couple[2][0], fontsize = "9")
a[0][3].bar(key_frequency_couple[3][1], key_frequency_couple[3][2], color = "#444444")
a[0][3].set_title(key_frequency_couple[3][0],fontsize = "9")
a[1][0].bar(key_frequency_couple[4][1], key_frequency_couple[4][2], color = "#444444")
a[1][0].set_title(key_frequency_couple[4][0],fontsize = "9")
a[1][1].bar(key_frequency_couple[5][1], key_frequency_couple[5][2], color = "#444444")
a[1][1].set_title(key_frequency_couple[5][0],fontsize = "9")
a[1][2].bar(key_frequency_couple[6][1], key_frequency_couple[6][2], color = "#444444")
a[1][2].set_title(key_frequency_couple[6][0],fontsize = "9")
a[1][3].bar(key_frequency_couple[7][1], key_frequency_couple[7][2], color = "#444444")
a[1][3].set_title(key_frequency_couple[7][0],fontsize = "9")
fig.suptitle("Anlık Frekans Histogramları")
fig.set_figheight(6)
fig.set_figwidth(12)
plt.show()