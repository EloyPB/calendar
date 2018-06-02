#!/usr/bin/env python3

import sys
import json
from datetime import datetime, date, timedelta


if len(sys.argv) == 1 or sys.argv[1] == "0":
    dayIndex = -1
else:
    if sys.argv[1][0] == "-":
        dayIndex = int(sys.argv[1])
    else:
        today = date.today()
        if datetime.now().hour < 21:
            today -= timedelta(days=1)
        editDate = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
        dayIndex = (editDate - today).days - 1

formats = {'sat': float, 'sharp': int, 'no-p': int, 'me-e': int, 'ph-e': int, 'food': str, 'exp': int,
           'mind': int, 'body': int, 'pain': bool, 'text': str, 'nourr': int}

print("\n            |---|---|---|---|---|---|---|---|---|---|")
print("            0   1   2   3   4   5   6   7   8   9   10\n")

with open('/media/DATA/MEGA/Calendar.json', 'r') as f:
    dataArray = json.load(f)

    for key in dataArray[dayIndex]:
        if key != 'date':
            prompt_string = key + " [" + str(dataArray[dayIndex][key]) + "] "
            dataArray[dayIndex][key] = formats[key](input(prompt_string) or dataArray[dayIndex][key])

    key = input("Something else?: ")
    if key in formats:
        dataArray[dayIndex][key] = formats[key](input(key + ": "))
    elif key != "":
        print("Key not recognized")

with open('/media/DATA/MEGA/Calendar.json', 'w') as f:
    json.dump(dataArray, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)

