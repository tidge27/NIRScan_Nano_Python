from os import walk
import json

existing = []
for (dirpath, dirnames, filenames) in walk("sesame-0000000000000001/Measurements/L1"):
    existing.extend(filenames)
    break
print(existing)
existing = [x for x in existing if not (x == ".DS_Store" or ".dat" in x)]
# exit()
print(existing)
existing_names = [int(file[-18: -5]) for file in existing]
number_name = list(zip(existing_names, existing))
number_name.sort()

newFile = open("export.csv", "w")

export_parameter_list = [
            "year",
            "month",
            "day",
            "day_of_week",
            "hour",
            "minute",
            "second",
            "system_temp_hundredths",
            "detector_temp_hundredths",
            "humidity_hundredths",
]


for count, i in enumerate(number_name):
    with open("sesame-0000000000000001/Measurements/L1/{}".format(i[1]), "r") as this_file:
        this_json = json.loads(this_file.read())
        if count == 0:
            newFile.write(
                "wavelength , " + ", ".join([str(len) for len in this_json["wavelength"][0:this_json["length"]]])
            )
            newFile.write("," + ", ".join(export_parameter_list) + "\n")

        newFile.write(
            str(i[1]) + ", " + ", ".join([str(len) for len in this_json["intensity"][0:this_json["length"]]])
        )
        newFile.write("," + ", ".join([str(this_json[param]) for param in export_parameter_list]) + "\n")