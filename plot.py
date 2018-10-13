#!/usr/bin/env python3

import sys
from my_calendar import Calendar


num_days = None
first_date = None
second_date = None

if len(sys.argv) == 3:
    first_date = sys.argv[1]
    second_date = sys.argv[2]
elif len(sys.argv) == 2:
    try:
        num_days = int(sys.argv[1])
    except ValueError:
        first_date = sys.argv[1]
else:
    num_days = 1

calendar = Calendar()
calendar.plot(num_days, first_date, second_date)
