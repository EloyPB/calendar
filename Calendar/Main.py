import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt

dates = []
happiness = []
pain = []
p = []
m = []
b = []
e = []

with open('notas.txt') as f:
    for line in f:
        painShift = 0
        dates.append(line.split()[0])
        happiness.append(float(line.split()[1].replace(',','.')))
        if line.split()[2] == "pain":
            pain.append(True)
            painShift= 1
        else:
            pain.append(False)
        p.append(line.split()[2+painShift])
        m.append(line.split()[3+painShift])
        b.append(line.split()[4+painShift])
        e.append(line.split()[5+painShift])
        
painCount = 0
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
        painHistogram[painCount] += 1
        
        painIntervals.append(painCount)
        painTimes.append(n)
        painIntervalInstance.append(painHistogram[painCount]-1)
        
        painCount = 1

painColor = np.zeros((max(painHistogram), len(painHistogram)))
for n, painInterval in enumerate(painIntervals):
    painColor[painIntervalInstance[n], painInterval] = painTimes[n]/max(painTimes)
painColorMasked = ma.masked_equal(painColor, 0)

# plt.figure()                        
# plt.plot(painHistogram, 'k+-')
# plt.title("pain histogram")

fig, ax = plt.subplots()
pc = ax.pcolormesh(painColorMasked)
cbar = fig.colorbar(pc, ticks=[np.min(painColorMasked), 1])
cbar.ax.set_yticklabels([dates[painTimes[0]], dates[painTimes[-1]]]) 
plt.show()