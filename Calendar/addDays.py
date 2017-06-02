import json
from datetime import datetime, date, timedelta
import calendar

today = date.today()

with open('Calendar.json', 'r') as f:
    dataArray = json.load(f)
    
    lastDate =  datetime.strptime(dataArray[-1]['fecha'], "%Y-%m-%d").date()
    daysMissing = today - lastDate
    if daysMissing.days == 0:
        print("El día de hoy ya está introducido.")
    for i in range(1, daysMissing.days + 1):
        date = lastDate + timedelta(days=i)
        print("Data for", calendar.day_name[date.weekday()], date)
        
        day = {'fecha' : str(date),
               'nota' : float(input("nota: ")),
               'no-p' : int(input("no-p: ")),
               'mind' : int(input("mind: ")),
               'body' : int(input("body: ")),
               'exp' : int(input("exp: ")),
               'pain' : True if input("pain (y/n): ")=='y' else False,
               'texto' : input("texto: ")
               }
        dataArray.append(day)
              
with open('Calendar.json', 'w') as f:
    json.dump(dataArray, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)

