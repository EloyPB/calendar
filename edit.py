#!/usr/bin/env python3

import sys
from my_calendar import Calendar


calendar = Calendar()

if len(sys.argv) > 1:
    calendar.edit(edit_date=sys.argv[1])
else:
    calendar.edit()

