#!/usr/bin/env python3

import sys
import json
from datetime import datetime

print("\n\n")

if len(sys.argv) == 2:
    num_days = int(sys.argv[-1])
else:
    num_days = 1

week_days = ["Lunes     ", "Martes    ", "Miércoles ", "Jueves    ", "Viernes   ", "Sábado    ", "Domingo   "]

with open('/media/DATA/MEGA/Calendar.json', 'r') as f:
    data_array = json.load(f)
    
    for day_num in range(num_days, 0, -1):
        day = data_array[-day_num]
        
        date = datetime.strptime(day['date'], "%Y-%m-%d").date()
        week_day = week_days[date.weekday()]

        pain = " PAIN," if day['pain'] else ""
        color = '\x1b[1;32m' if day['sat'] >= 5 else '\x1b[1;31m'

        string = week_day + day['date'] + "  " + color + str(day['sat']) + '\x1b[0m'
        if day['pain']:
            string += '\x1b[1;34m' + "  PAIN  " + '\x1b[0m'
        else:
            string += "        "

        brown = '\x1b[0;33m'
        for key in day:
            if key not in ('date', 'pain', 'sat'):
                string += key + ": " + brown + str(day[key]) + '\x1b[0m' + "  "

        print(string + "\n")

print("\n\n")
