#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime as dt

dates = []
intervals = []

with open('dates.txt') as file:
    for n, line in enumerate(file):
        date = dt.strptime(line.strip(), "%d/%m/%Y").date()

        if n > 0:
            dates.append(date)
            intervals.append((date-previous_date).days)

        previous_date = date

dumb_dates = [(date-dates[0]).days for date in dates]
total_days = dumb_dates[-1]


while True:
    option = input("\ncolourful (h)istogram, (p)ercentiles or (q)uit: ")

    if option == "q":
        exit()

    elif option == "h":
        histogram = []
        intervals_count = []
        for interval in intervals:
            while interval >= len(histogram):
                histogram.append(0)
            intervals_count.append(histogram[interval])
            histogram[interval] += 1

        colors = np.zeros((max(histogram), len(histogram)))

        for n, interval in enumerate(intervals):
            colors[intervals_count[n], interval] = dumb_dates[n]/total_days
        masked_colors = np.ma.masked_equal(colors, 0)

        fig, ax = plt.subplots()
        pc = ax.pcolormesh(masked_colors)
        cbar = fig.colorbar(pc, ticks=[np.min(masked_colors),1])
        cbar.ax.set_yticklabels([dates[0], dates[-1]])
        plt.show(block=False)

    elif option == "p":
        while True:
            try:
                window_size = int(input("Enter the size of the sliding window in days: "))
                break
            except ValueError:
                print("You can do better, Laia")

        dumb_dates = np.array(dumb_dates)
        intervals = np.array(intervals)
        percentiles = [0, 25, 50, 75, 100]
        p = np.zeros((len(percentiles), total_days - window_size))

        for start in range(0, total_days - window_size):
            window = intervals[(dumb_dates >= start) & (dumb_dates <= start + window_size)]
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

        ax.set_title("Percentiles in a sliding window of "+ str(window_size) + " days")
        plt.show(block=False)