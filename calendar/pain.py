#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import json

with open('/media/eloy/OS/Users/Eloy/OneDrive/Calendar.json', 'r') as f:
    days = json.load(f)
    num_days = len(days)

count = -2
histogram = []
times = []
intervals = []
intervals_counts = []
years = []

for n, day in enumerate(days):
    count += 1
    if day['pain']:
        while count >= len(histogram):
            histogram.append(0)
        if count > 0:
            times.append(n)
            intervals.append(count)
            intervals_counts.append(histogram[count])
            histogram[count] += 1
        count = 0
    if day['fecha'][5:] == '01-01':
        years.append((n, day['fecha'][:4]))

print("\nCurrent count: {} days".format(count))
higher_than = sum(histogram[:count])
lower_than = sum(histogram[count+1:])
total = sum(histogram)
print("Higher than ", round(higher_than/total*100, 2), " and lower than ", round(lower_than/total*100, 2))

while True:
    option = input("\n(q)uit, (h)istogram or (p)ercentiles: ")

    if option == "q":
        exit()

    elif option == "h":
        colors = np.zeros((max(histogram), len(histogram)))

        for n, time in enumerate(times):
            colors[intervals_counts[n], intervals[n]] = time/num_days
        masked_colors = np.ma.masked_equal(colors, 0)

        fig, ax = plt.subplots()
        pc = ax.pcolormesh(masked_colors)
        cbar = fig.colorbar(pc, ticks=np.linspace(years[0][0]/num_days, years[-1][0]/num_days, len(years)))
        cbar.ax.set_yticklabels([year[1] for year in years])
        plt.show(block=False)

    elif option == "p":
        while True:
            try:
                window_size = int(input("Enter the size of the sliding window in days: [365] ") or 365)
                break
            except ValueError:
                print("Give me a number")

        times = np.array(times)
        intervals = np.array(intervals)
        percentiles = [0, 25, 50, 75, 100]
        p = np.zeros((len(percentiles), num_days - window_size))

        for start in range(0, num_days - window_size):
            window = intervals[(times >= start) & (times <= start + window_size)]
            for i, percentile in enumerate(percentiles):
                p[i, start] = np.percentile(window, percentile)

        fig, ax = plt.subplots(1)
        ax.fill_between(range(p[0].size), p[0], p[4], facecolor='C7', alpha=0.2)
        ax.fill_between(range(p[0].size), p[1], p[3], facecolor='C7', alpha=0.4)
        ax.plot(p[4], 'C7', label='100%', alpha=0.4)
        ax.plot(p[3], 'C7', label ='75%')
        ax.plot(p[2], 'k', label ='50%')
        ax.plot(p[1], 'C7', label ='25%')
        ax.plot(p[0], 'C7', label='0%', alpha=0.4)
        ax.legend()

        ticks = []
        labels = []
        for year in years:
            if window_size/2 < year[0] < num_days - window_size/2:
                ticks.append(year[0] - window_size/2)
                labels.append(year[1])

        ax.set_xticks(ticks)
        ax.set_xticklabels(labels)

        ax.set_title("Percentiles in a sliding window of "+ str(window_size) + " days")
        plt.show(block=False)






