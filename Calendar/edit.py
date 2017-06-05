#!/usr/bin/env python3

import sys
import json
from datetime import datetime, date, timedelta

if len(sys.argv) == 1 or sys.argv[1] == "today" or "0":
    dayIndex = -1
else:
    if sys.argv[1] == "yesterday":
        dayIndex = -2
    elif sys.argv[1][0] == "-":
        dayIndex = sys.argv[1]
    else:
        today = date.today()
        if datetime.now().hour < 7:
            today -= timedelta(days=1)
        editDate = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
        dayIndex = (editDate - today).days -1


with open('Calendar.json', 'r') as f:
    dataArray = json.load(f)
    
    day = {'fecha' : dataArray[dayIndex]['fecha'],
           'nota' : float(input("nota ["+str(dataArray[dayIndex]['nota'])+"] ") or dataArray[dayIndex]['nota']),
           'no-p' : int(input("no-p ["+str(dataArray[dayIndex]['no-p'])+"] ") or dataArray[dayIndex]['no-p']),
           'mind' : int(input("mind ["+str(dataArray[dayIndex]['mind'])+"] ") or dataArray[dayIndex]['mind']),
           'body' : int(input("body ["+str(dataArray[dayIndex]['body'])+"] ") or dataArray[dayIndex]['body']),
           'exp' : int(input("exp ["+str(dataArray[dayIndex]['exp'])+"] ") or dataArray[dayIndex]['exp']),
           'pain' : (input("pain ["+("y] " if dataArray[dayIndex]['pain'] else "n] ")) or ("y" if dataArray[dayIndex]['pain'] else "n")) == "y",
           'texto' : input("texto ["+dataArray[dayIndex]['texto']+"] ") or dataArray[dayIndex]['texto']
           }
    dataArray[dayIndex] = day

with open('Calendar.json', 'w') as f:
    json.dump(dataArray, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)

