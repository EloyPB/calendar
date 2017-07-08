#!/usr/bin/env python3

import json

with open('/media/eloy/OS/Users/Eloy/OneDrive/Calendar.json', 'r') as f:
    dataArray = json.load(f)
    count = 1
    while(dataArray[-count]['pain'] == False):
        count += 1
    print(count-1)


