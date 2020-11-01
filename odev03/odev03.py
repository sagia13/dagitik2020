
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
        sensor_transmittor_couples[sensor + ":" + transmittor] = []
        for data in datalist:
            if data[1] == sensor and data[2] == transmittor:
                numeric_data = int(data[3].replace("\n",""))
                sensor_transmittor_couples[sensor + ":" + transmittor].append(numeric_data)


        