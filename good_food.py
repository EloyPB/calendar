#!/usr/bin/env python3

import sys
import json
import numpy as np
from scipy.stats.stats import pearsonr
import matplotlib.pyplot as plt
import math

if len(sys.argv) == 2:
    correlation_depth = int(sys.argv[-1])
else:
    correlation_depth = 5

with open('/media/DATA/MEGA/Calendar.json', 'r') as f:
    data = json.load(f)
    first_record = 2345

    # get the list of foods and how many times each of them appears
    food_list_unsorted = []
    food_counts_unsorted = []
    for day in data[first_record:]:
        for food in day['food'].split(", "):
            if food in food_list_unsorted:
                food_counts_unsorted[food_list_unsorted.index(food)] += 1
            else:
                food_list_unsorted.append(food)
                food_counts_unsorted.append(1)

    # sort foods by frequency
    food_list = []
    food_counts = []
    sorted_indices = np.flip(np.argsort(food_counts_unsorted), 0)
    for sorted_index in sorted_indices:
        food_list.append(food_list_unsorted[sorted_index])
        food_counts.append(food_counts_unsorted[sorted_index])

    for food, count in zip(food_list, food_counts):
        print(food, count)

    # create matrix
    num_days = len(data) - first_record
    print(num_days)
    num_foods = len(food_list)
    mat = np.zeros((num_days, num_foods))

    sharp = np.zeros(num_days)
    sat = np.zeros(num_days)

    for day_num, day in enumerate(data[first_record:]):
        sharp[day_num] = day['sharp']
        sat[day_num] = day['sat']
        for food_num, food in enumerate(food_list):
            if food in day['food'].split(", "):
                mat[day_num, food_num] = 1

    # calculate correlations
    sharp_corr = np.zeros((num_foods, correlation_depth))
    sat_corr = np.zeros((num_foods, correlation_depth))

    for food_num in range(num_foods):
        for shift in range(0, correlation_depth):
            sharp_corr[food_num, shift] = pearsonr(mat[0:num_days-shift,food_num], sharp[shift:])[0]
            sat_corr[food_num, shift] = pearsonr(mat[0:num_days-shift,food_num], sat[shift:])[0]

    # plot
    num_rows = 25
    num_cols = min(math.ceil(num_foods/num_rows), 5)
    sharp_corr = np.pad(sharp_corr, ((0, max(num_rows*num_cols-num_foods, 0)), (0, 0)), 'constant', constant_values=np.nan)

    fig, ax = plt.subplots(1, num_cols)
    for col_num in range(num_cols):
        first_index = col_num*num_rows
        last_index = (col_num+1)*num_rows
        im = ax[col_num].matshow(sharp_corr[first_index:last_index], vmin=-1, vmax=1)
        ax[col_num].set_yticks([i for i in range(num_rows)])
        ax[col_num].set_yticklabels(food_list[first_index:last_index])

    # fig, ax = plt.subplots(1, num_cols)
    # for col_num in range(num_cols):
    #     first_index = col_num*num_rows
    #     last_index = min((col_num+1)*num_rows, num_foods)
    #     im = ax[col_num].matshow(sat_corr[first_index:last_index], vmin=-1, vmax=1)
    #     ax[col_num].set_yticks([i for i in range(num_rows)])
    #     ax[col_num].set_yticklabels(food_list[first_index:last_index])

    # fig.colorbar(im, ax=ax.ravel().tolist(), shrink=0.5)
    plt.show()


