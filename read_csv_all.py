import pandas
import matplotlib
import matplotlib.pyplot as plt
import datetime
from os import walk

matplotlib.use('TkAgg')

existing = []
for (dirpath, dirnames, filenames) in walk("sesame-0000000000000002-master/Measurements/CISS"):
    existing.extend(filenames)
    break
print(existing)
existing = [x for x in existing if not (x == ".DS_Store" or ".dat" in x)]

frames = []
for file in existing:
    frames.append(pandas.read_csv("sesame-0000000000000002-master/Measurements/CISS/{}".format(file), skiprows=1, usecols=[1, 11, 12, 13], names=["timestamp", "temp", "pres", "humi"]))

# df1 = pandas.read_csv("sesame-0000000000000002/Measurements/L0/CISS_measurements_start_heat_up.csv", usecols=[1, 11, 12, 13], names=["timestamp", "temp", "pres", "humi"])
# df1 = df1[1:]
#
# df2 = pandas.read_csv("sesame-0000000000000003/Measurements/L0/CISS_measurements.csv", usecols=[1, 11, 12, 13], names=["timestamp", "temp", "pres", "humi"])
# df2 = df2[1:]

df = pandas.concat(frames)
df = df.dropna(subset=['temp'])
# df['time'] = pandas.to_datetime(df['timestamp'], unit="ms")

df['time'] = pandas.to_datetime(df['timestamp'].astype(int),unit="ms")



# df['time_from_start'] = pandas.to_timedelta(
#     [n - df['timestamp'][1] for n in df['timestamp']],
#     unit="ms"
# )

# time_from_start = datetime.timedelta(milliseconds=(timestamp - t0))

# matplotlib.use('MacOSX')

df["temp"] = df["temp"].astype(float)
df["pres"] = df["pres"].astype(float)
df["humi"] = df["humi"].astype(float)


# ax = plt.gca()
tfig, tax = plt.subplots(1)

df.plot(x="time", y="temp", ax=tax)
df.plot(x="time", y="humi", ax=tax)
df.plot(x="time", y="pres", ax=tax, marker='o')

tfig.autofmt_xdate()



import matplotlib.dates as mdates
# ax.fmt_xdata = mdates.DateFormatter('%h-%M-%s')
# df.plot(x="time", y="axg2", ax=ax)
# df.plot(x="time", y="axg4", ax=ax)

# df.plot(x="timestamp", y="pres", ax=ax, marker='o')
# df.plot(x="timestamp", y="ay")

# df.plot(x="timestamp", y="humi", ax=ax, marker='o')

plt.show()

print(df)