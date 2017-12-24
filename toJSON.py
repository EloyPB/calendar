import json
import matplotlib.pyplot as plt

dataArray = []
months = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06',
          'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}

with open('todo.txt') as f:
    for line in f:
        
        fecha_excel = line.split()[0]
        dia = fecha_excel.split('-')[0]
        if len(dia) == 1:
            dia = '0'+dia
        mes = months[fecha_excel.split('-')[1]]
        anio = '20'+fecha_excel.split('-')[2]
        fecha = anio+'-'+mes+'-'+dia
        
        painShift = 0
        if line.split()[2] == "pain":
            painShift= 1
            pain = True
        else:
            pain = False
            
        if len(line.split())-painShift > 6:
            texto = line[line.index(line.split()[6+painShift]):]
        else:
            texto = ""
            
        day = {'fecha' : fecha,
               'nota' : float(line.split()[1].replace(',','.')),
               'pain' : pain,
               'no-p' : int(line.split()[2+painShift]),
               'mind' : int(line.split()[3+painShift]),
               'body' : int(line.split()[4+painShift]),
               'exp' : int(line.split()[5+painShift]),
               'texto' : texto
               }
        dataArray.append(day)
          
with open('CalendarNEW.json', 'w') as f:
    json.dump(dataArray, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
  
with open('CalendarNEW.json', 'r') as f:
    dataArray = json.load(f)

plt.plot([day['nota'] for day in dataArray])
plt.grid(True)
plt.show()