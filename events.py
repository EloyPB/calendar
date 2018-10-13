#!/usr/bin/env python3

import sys
from my_calendar import Calendar

if len(sys.argv) < 2:
    print("Indicate the name of the field")
    sys.exit()

calendar = Calendar()
calendar.events(sys.argv[1])
