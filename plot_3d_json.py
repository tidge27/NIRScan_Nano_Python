from os import walk
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D


matplotlib.use('TkAgg')


existing = []
for (dirpath, dirnames, filenames) in walk("sesame-0000000000000002-master/Measurements/Spectrometer"):
    existing.extend(filenames)
    break
print(existing)

existing = [x for x in existing if (".JSON" in x)]
# exit()
print(existing)


existing_names = [int(file[-18: -5]) for file in existing]
number_name = list(zip(existing_names, existing))
number_name.sort()
#
# newFile = open("export.csv", "w")

# export_parameter_list = [
#             "year",
#             "month",
#             "day",
#             "day_of_week",
#             "hour",
#             "minute",
#             "second",
#             "system_temp_hundredths",
#             "detector_temp_hundredths",
#             "humidity_hundredths",
# ]
x = []
y = []
z = []

for count, i in enumerate(number_name):
    print(count)
    with open("sesame-0000000000000002-master/Measurements/Spectrometer/{}".format(i[1]), "r") as this_file:
        this_json = json.loads(this_file.read())
        if count == 0:
            z.extend([int(len) for len in this_json["intensity"][0:this_json["length"]]])
            y.extend([int(len) for len in this_json["wavelength"][0:this_json["length"]]])
        else:
            for colcount, col in enumerate(z):
                z[colcount] += this_json["intensity"][colcount]


        # x.extend([i[0]]*this_json["length"])

print(x)
print(y)
print(z)

X = np.array(x)
Y = np.array(y)
Z = np.array(z)

        # newFile.write(
        #     str(i[1]) + ", " + ", ".join([str(len) for len in this_json["intensity"][0:this_json["length"]]])
        # )
        # newFile.write("," + ", ".join([str(this_json[param]) for param in export_parameter_list]) + "\n")


fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(Y, Z, 'gray')

plt.show()