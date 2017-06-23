#!/usr/bin/env python3

import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import json

with open('/media/eloy/OS/Users/Eloy/OneDrive/Calendar.json', 'r') as f:
    dataArray = json.load(f)
    pain = [day['pain'] for day in dataArray]
        
painCount = -2
painHistogram = []
painIntervals = []
painIntervalInstance = []
painTimes = []

for n, x in enumerate(pain):
    if x == False:
        painCount += 1
    else:
        while painCount >= len(painHistogram):
            painHistogram.append(0)
        
        if painCount >= 0:
            painHistogram[painCount] += 1
        
            painIntervals.append(painCount)
            painTimes.append(n)
            painIntervalInstance.append(painHistogram[painCount]-1)
        
        painCount = 1

painColor = np.zeros((max(painHistogram), len(painHistogram)))
for n, painInterval in enumerate(painIntervals):
    painColor[painIntervalInstance[n], painInterval] = painTimes[n]/max(painTimes)
painColorMasked = ma.masked_equal(painColor, 0)


fig, ax = plt.subplots()
pc = ax.pcolormesh(painColorMasked)
cbar = fig.colorbar(pc, ticks=[np.min(painColorMasked), 1])
cbar.ax.set_yticklabels([dataArray[painTimes[0]]['fecha'], dataArray[painTimes[-1]]['fecha']]) 
plt.show()