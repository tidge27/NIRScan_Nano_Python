import pandas
import matplotlib
import matplotlib.pyplot as plt
import datetime

plt.figure()

df = pandas.read_csv("CISS_measurements_print_accel.csv", usecols=[1,2,3], names=["timestamp", "ax", "ay"])
# df['time'] = pandas.to_datetime(df['timestamp'], unit="ms")

df['time'] = pandas.to_datetime(
    [n - df['timestamp'][1] for n in df['timestamp']],
    unit="ms"
)

df['ax'] = (df['ax'] - int(df['ax'].mean())).abs()
df['ay'] = (df['ay'] - int(df['ay'].mean())).abs()

df['axg2'] = 20*df['ax'].rolling(512, win_type='gaussian', ).mean(std=512)
# df['axg4'] = 10*df['ax'].rolling(2048, win_type='gaussian', ).mean(std=2048)
df['axg4'] = 20*df['ax'].rolling(512, win_type='gaussian', ).mean(std=512).rolling(512, win_type='gaussian', ).mean(std=512)

df['axg2'] = (df['axg2'] - int(df['axg2'].mean()))
df['axg4'] = (df['axg4'] - int(df['axg4'].mean()))

df['ayx'] = (df['ax'] +df['ay'])


# df['time_from_start'] = pandas.to_timedelta(
#     [n - df['timestamp'][1] for n in df['timestamp']],
#     unit="ms"
# )

# time_from_start = datetime.timedelta(milliseconds=(timestamp - t0))

matplotlib.use('MacOSX')

ax = plt.gca()
df.plot(x="time", y="ax", ax=ax)
# df.plot(x="time", y="axg2", ax=ax)
# df.plot(x="time", y="axg4", ax=ax)

df.plot(x="time", y="ay", ax=ax)
# df.plot(x="timestamp", y="ay")

df.plot(x="time", y="ayx", ax=ax)

plt.show()

print(df)