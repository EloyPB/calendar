from datetime import datetime
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

for day in calendar.database:
    if "pain" in day:
        if day["pain"]:
            g.date = datetime.strptime(f"{day['date']} 12:00", "%Y-%m-%d %H:%M")
            m.compute(g)
            moon_phases.append(m.moon_phase)

print(moon_phases[-1])
plt.hist(moon_phases, bins=12)
plt.xlabel("Moon phase")
plt.ylabel("Migraine count")

plt.tight_layout()
plt.show()
