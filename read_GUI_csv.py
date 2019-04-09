import pandas
import matplotlib
import matplotlib.pyplot as plt
import datetime

matplotlib.use('TkAgg')


# This reads

mix = pandas.read_csv(
    "initialtestreadingswithtalcandnylonpowder/mixHadamard 1_063003_20190226_071616.csv",
    skiprows=22, names=["wavelength", "absorbance", "reference", "sample"]
)
nylon = pandas.read_csv(
    "initialtestreadingswithtalcandnylonpowder/nylonHadamard 1_063002_20190226_071250.csv",
    skiprows=22, names=["wavelength", "absorbance", "reference", "sample"]
)
talc = pandas.read_csv(
    "initialtestreadingswithtalcandnylonpowder/talcHadamard 1_063001_20190226_070716.csv",
    skiprows=22, names=["wavelength", "absorbance", "reference", "sample"]
)



count = 0
best_squares = 0
best_squares_index = 0
best_squares_offset = 0
squares_dict = {}
for offset in range(-100, 100):
    print(offset)
    for i in range(40,60):
        squares = 0
        pred_abs_list = []
        for index, row in mix.iterrows():
            pred_abs = (i/100)*talc['absorbance'][index] + ((100-i)/100)*nylon['absorbance'][index] + 0.01*offset/100
            pred_abs_list.append(pred_abs)
            squares += (mix['absorbance'][index] - pred_abs)**2
        if squares < best_squares or count==0:
            best_squares = squares
            best_squares_index = i
            best_squares_offset = offset
        squares_dict[str(i)] = squares
        mix[str("percent_{}_offset_{}".format(i, offset))] = pred_abs_list
        count+=1

print("{}% Talc".format(best_squares_index))

tfig, tax = plt.subplots(1)

mix.plot(x="wavelength", y="absorbance", ax=tax)
mix.plot(x="wavelength", y=str("percent_{}_offset_{}".format(best_squares_index, best_squares_offset)), ax=tax)

# mix.plot(x="wavelength", y="percent_49", ax=tax)
# mix.plot(x="wavelength", y="percent_50", ax=tax)
# mix.plot(x="wavelength", y="percent_51", ax=tax)

nylon.plot(x="wavelength", y="absorbance", ax=tax)
talc.plot(x="wavelength", y="absorbance", ax=tax)


plt.show()