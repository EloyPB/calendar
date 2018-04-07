#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime, date, timedelta

with open('/media/DATA/MEGA/Calendar.json', 'r') as f:
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
    option = input("\n(q)uit, (h)istogram, (p)ercentiles or (n)ormalized periods: ")

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

    elif option == "n":
        first_date = datetime.strptime(days[0]['fecha'], "%Y-%m-%d").date()
        start_date = datetime.strptime("2015-08-13", "%Y-%m-%d").date()
        start_index = (start_date - first_date).days

        found_pain = False
        index = -1
        while not found_pain:
            if days[index]['pain']:
                found_pain = True
            else:
                index -= 1
        end_index = len(days) + index

        periods = []
        new_period = []
        for day in days[start_index:end_index+1]:
            new_period.append(day['nota'])
            if day['pain']:
                periods.append(new_period)
                new_period = []

        max_length = 0
        for period in periods:
            if len(period) > max_length:
                max_length = len(period)

        normalized = np.zeros((len(periods), max_length))

        interpolate = False

        for period_num, period in enumerate(periods):
            for i in range(max_length):
                ii = i/(max_length - 1)
                x = ii*(len(period)-1)

                if interpolate:
                    x_low = int(x)
                    x_high = int(x) + 1
                    low_ratio = x_high - x
                    high_ratio = x - x_low
                    x_high = min(x_high, len(period)-1)
                    normalized[period_num, i] = period[x_low]*low_ratio + period[x_high]*high_ratio
                else:
                    normalized[period_num, i] = period[round(x)]

        mean = np.mean(normalized, 0)
        std = np.std(normalized, 0)

        x_axis = np.linspace(0, 1, max_length)
        plt.plot(x_axis, mean)

        plt.figure()
        plt.plot(x_axis, std)
        plt.show()










