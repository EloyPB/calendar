#!/usr/bin/env python3

import json
from datetime import datetime, date, timedelta
import calendar

today = date.today()
if datetime.now().hour < 20:
    today -= timedelta(days=1)

with open('/media/DATA/MEGA/Calendar.json', 'r') as f:
    dataArray = json.load(f)
    
    lastDate = datetime.strptime(dataArray[-1]['fecha'], "%Y-%m-%d").date()
    daysMissing = today - lastDate
    if daysMissing.days == 0:
        print("\nYa está hecho.\n")

    for i in range(1, daysMissing.days + 1):
        date = lastDate + timedelta(days=i)
        print("Data for", calendar.day_name[date.weekday()], date, "\n")
        print("            |---|---|---|---|---|---|---|---|---|---|")
        print("            0   1   2   3   4   5   6   7   8   9   10\n")

        while True:
            try:
                nota = float(input("nota: "))
                break
            except ValueError:
                print("Give me a number please")

        values = []
        labels = ["sharp: ", "no-p: ", "me-ex: ", "ph-ex: ", "food: ", "exp: "]
        for label in labels:
            while True:
                try:
                    values.append(int(input(label)))
                    break
                except ValueError:
                    print("Give me a number please")

        day = {'fecha': str(date),
               'sharp': values[0],
               'no-p': values[1],
               'nota': nota,
               'me-e': values[2],
               'ph-e': values[3],
               'food': values[4],
               'exp': values[5],
               'pain': True if input("pain? [n]: ") == 'y' else False,
               'texto': input("texto: ")
               }
        dataArray.append(day)
              
with open('/media/DATA/MEGA/Calendar.json', 'w') as f:
    json.dump(dataArray, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)

