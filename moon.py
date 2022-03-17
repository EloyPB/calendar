import numpy as np
from datetime import datetime, timedelta
import ephem
import matplotlib.pyplot as plt
from my_calendar import Calendar


calendar = Calendar()

g = ephem.Observer()
g.name = 'sevilla'
g.lat = 37.3891
g.long = 5.9845

m = ephem.Moon()

moon_phases = []
lunations = []

for day in calendar.database:
    if "pain" in day:
        if day["pain"]:
            g.date = datetime.strptime(f"{day['date']} 12:00", "%Y-%m-%d %H:%M")
            m.compute(g)
            moon_phases.append(m.moon_phase)

            nnm = ephem.next_new_moon(g.date)
            pnm = ephem.previous_new_moon(g.date)
            lunation = (g.date - pnm) / (nnm - pnm)
            lunations.append(lunation)

print(moon_phases[-1])
n, bins, _ = plt.hist(moon_phases, bins=12)
plt.xlabel("Visible fraction")
plt.ylabel("Migraine count")
plt.tight_layout()

plt.figure()
plt.hist(lunations)
plt.xlabel("Lunar phase")
plt.ylabel("Migraine count")

plt.figure()
plt.plot(lunations, moon_phases, '.')
plt.xlabel("Lunar phase")
plt.ylabel("Visible fraction")

# bin_centers = np.mean(np.array((bins[:-1], bins[1:])), axis=0) * 2 * np.pi
# fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
# ax.plot(np.append(bin_centers, bin_centers[0]), np.append(n, [n[0]]), 'o-')


plt.show()
