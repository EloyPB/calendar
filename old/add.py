#!/usr/bin/env python3

import json
from datetime import datetime, date, timedelta
import calendar


def get_value(key, is_of_type):
    while True:
        try:
            value = is_of_type(input(key))
            break
        except ValueError:
            print("Give me a number")
    return value


today = date.today()
if datetime.now().hour < 20:
    today -= timedelta(days=1)

with open('/media/DATA/MEGA/Calendar.json', 'r') as f:
    dataArray = json.load(f)
    
    lastDate = datetime.strptime(dataArray[-1]['date'], "%Y-%m-%d").date()
    daysMissing = today - lastDate
    if daysMissing.days == 0:
        print("\nNothing to add\n")

    for i in range(1, daysMissing.days + 1):
        date = lastDate + timedelta(days=i)
        print("Data for", calendar.day_name[date.weekday()], date, "\n")
        print("            |---|---|---|---|---|---|---|---|---|---|")
        print("            0   1   2   3   4   5   6   7   8   9   10\n")

        day = {'date': str(date),
               'sat': get_value('sat: ', float),
               'ph-e': get_value('phys: ', int),
               'exp': get_value('exp: ', int),
               'sharp': get_value('sharp: ', int),
               'food': input('food: '),
               }
        text = input('text: ')
        day['pain'] = True if "PAIN" in text else False
        if text != "":
            day['text'] = text

        dataArray.append(day)
              
with open('/media/DATA/MEGA/Calendar.json', 'w') as f:
    json.dump(dataArray, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)

