#!/usr/bin/env python3

import sys
import json
from datetime import datetime

if(len(sys.argv) != 2):
    print("Indíca cuántos días quieres que imprima!")
    quit()

print("\n\n")
numDays = int(sys.argv[-1])
diasdelasemana = ["Lunes     ", "Martes    ", "Miércoles ", "Jueves    ", "Viernes   ", "Sábado    ", "Domingo   "]

with open('/media/eloy/OS/Users/Eloy/OneDrive/Calendar.json', 'r') as f:
    dataArray = json.load(f)
    
    for dayNum in range(numDays,0,-1):
        day = dataArray[-dayNum]
        
        date =  datetime.strptime(day['fecha'], "%Y-%m-%d").date()
        diasemana =  diasdelasemana[date.weekday()]

        pain = " pain " if day['pain'] else ""
        color = '\x1b[1;32;40m' if day['nota'] >= 5 else '\x1b[1;31;40m'
        print(diasemana, day['fecha'], "", color+str(day['nota'])+'\x1b[0m', pain, day['no-p'], 
              day['mind'], day['body'], day['exp'], "", day['texto'], "\n")


print("\n\n")