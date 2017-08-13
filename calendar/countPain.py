#!/usr/bin/env python3

import json

with open('/media/eloy/OS/Users/Eloy/OneDrive/Calendar.json', 'r') as f:

    dataArray = json.load(f)
    
    pain = [day['pain'] for day in dataArray]
        
    painCount = -2
    painHistogram = []

    for x in pain:
        if x == False:
            painCount += 1
        else:
            while painCount >= len(painHistogram):
                painHistogram.append(0)
            
            if painCount >= 0:
                painHistogram[painCount] += 1

            painCount = 1
    
    
    currentCount = 1
    while(dataArray[-currentCount]['pain'] == False):
        currentCount += 1
    currentCount -= 1
    
    print("\nCurrent count: {} days".format(currentCount))
    higherThan = sum(painHistogram[:currentCount])
    lowerThan = sum(painHistogram[currentCount+1:])
    total = sum(painHistogram)
    print('Higher than {}% and lower than {}% of the times\n'.format(round(higherThan/total*100, 2), 
                                                                     round(lowerThan/total*100, 2)))


