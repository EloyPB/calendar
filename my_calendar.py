import json
import calendar
import tempfile, os
import numpy as np
import matplotlib.pyplot as plt
from pydoc import locate
from subprocess import call
from datetime import date, datetime, timedelta


def get_value(field, cast_type):
    while True:
        try:
            value = cast_type(input(field + ': '))
            break
        except ValueError:
            print("Expecting " + str(cast_type))
    return value


class Calendar:
    def __init__(self):
        with open('config.txt') as f:
            lines = [line.rstrip('\n') for line in f]

        self.path = lines[0]
        self.explicit_fields = []
        self.explicit_types = []
        self.implicit_fields = []
        self.implicit_sources = []
        self.implicit_keys = []

        for line in lines[1:]:
            words = line.split()
            if words[1] == 'implicit':
                self.implicit_fields.append(words[0])
                self.implicit_sources.append(words[2].split(':')[0])
                self.implicit_keys.append(words[2].split(':')[1])
            else:
                self.explicit_fields.append(words[0])
                self.explicit_types.append(locate(words[1]))

        with open(self.path, 'r') as f:
            self.database = json.load(f)

    def dump(self):
        with open(self.path, 'w') as f:
            json.dump(self.database, f, indent=4, separators=(',', ': '), ensure_ascii=False)

    def reorder(self):
        """Reorder database in the following way:
        1 - explicit fields mentioned in config file
        2 - implicit fields mentioned in config file
        3 - fields not mentioned in config file"""

        new_database = []
        for day in self.database:
            new_day = {'date': day['date']}
            for field in self.explicit_fields:
                if field in day:
                    new_day[field] = day[field]
            for field in self.implicit_fields:
                if field in day:
                    new_day[field] = day[field]
            for field in day:
                if field not in self.explicit_fields and field not in self.implicit_fields:
                    new_day[field] = day[field]
            new_database.append(new_day)

        self.database = new_database
        self.dump()

    def add_days(self):
        print("\n")
        # find out current date, if it is before 20:00 the current day does not count
        date_today = date.today()
        if datetime.now().hour < 20:
            date_today -= timedelta(days=1)

        # calculate how many days are missing
        last_date = datetime.strptime(self.database[-1]['date'], "%Y-%m-%d").date()
        days_missing = (date_today - last_date).days
        if days_missing == 0:
            print("\nAlready up to date\n")

        # get the information for each of the missing days
        for i in range(1, days_missing + 1):
            processing_date = last_date + timedelta(days=i)
            print("Data for", calendar.day_name[processing_date.weekday()], processing_date, "\n")
            # if any of the fields expects a number, print a scale from 0 to 10 as a visual aid
            if int in self.explicit_types or float in self.explicit_types:
                print("            |---|---|---|---|---|---|---|---|---|---|")
                print("            0   1   2   3   4   5   6   7   8   9   10\n")

            day = {'date': str(processing_date)}
            for field_num, field in enumerate(self.explicit_fields):
                value = get_value(field, self.explicit_types[field_num])
                day[field] = value
            for field_num, implicit_field in enumerate(self.implicit_fields):
                day[implicit_field] = self.implicit_keys[field_num] in day[self.implicit_sources[field_num]]

            self.database.append(day)

        self.dump()
        print("\n")

    def date_to_index(self, processing_date):
        first_date = datetime.strptime(self.database[0]['date'], "%Y-%m-%d").date()
        processing_date = datetime.strptime(processing_date, "%Y-%m-%d").date()
        last_date = datetime.strptime(self.database[-1]['date'], "%Y-%m-%d").date()
        if first_date < processing_date < last_date:
            return (processing_date - first_date).days
        else:
            print("Date out of range")

    def edit(self, edit_date=None):
        if edit_date is not None:
            edit_index = self.date_to_index(edit_date)
        else:
            edit_index = -1

        day = json.dumps(self.database[edit_index], indent=4, separators=(',', ': '), ensure_ascii=False)

        with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
            tf.write(bytes(day, 'utf-8'))
            tf.flush()
            editor = os.environ.get('EDITOR', 'vim')
            call([editor, tf.name])

            tf.seek(0)
            edited_day = json.loads(tf.read())
            self.database[edit_index] = edited_day

        self.dump()

    def index_range(self, num_days=None, first_date=None, last_date=None):
        if num_days is not None:
            first_index = -num_days
            last_index = 0
        else:
            first_index = self.date_to_index(first_date)
            if last_date is not None:
                last_index = self.date_to_index(last_date) + 1
            else:
                last_index = len(self.database)
        return first_index, last_index

    def display(self, num_days=None, first_date=None, last_date=None):
        print("\n")

        week_days = ["Monday    ", "Tuesday   ", "Wednesday ", "Thursday  ",
                     "Friday    ", "Saturday  ", "Sunday    "]

        brown = '\033[38;5;180m'
        blue = '\033[38;5;153m'
        reset = '\033[0m'

        first_index, last_index = self.index_range(num_days, first_date, last_date)

        for day_index in range(first_index, last_index):
            day = self.database[day_index]
            processing_date = datetime.strptime(day['date'], "%Y-%m-%d").date()
            week_day = week_days[processing_date.weekday()]

            string = week_day + day['date'] + "  "
            for field in self.explicit_fields:
                if field in day:
                    value = day[field]
                    if type(value) is str:
                        # print strings in light brown, with implicit field keywords in light blue
                        string += '\n' + field + ': '
                        words = value.split()
                        for word in words:
                            if word in self.implicit_keys:
                                string += blue + word + reset + ' '
                            else:
                                string += brown + word + reset + ' '
                    elif type(value) is int or type(value) is float:
                        # print numbers following color gradient from 0:white to 10:green
                        rb = str(int((10 - value) * 25.5))
                        color = '\033[38;2;' + rb + ';255;' + rb + 'm'
                        string += field + ': ' + color + str(value) + reset + ' '

            print(string + '\n')

        print("\n")

    def plot(self, num_days=None, first_date=None, last_date=None):
        first_index, last_index = self.index_range(num_days, first_date, last_date)
        try:
            with open('plots.txt') as f:
                plots = json.load(f)

                for plot in plots:
                    fig, ax = plt.subplots()
                    ax.set_ylim(0, 10)
                    ax.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
                    ax.yaxis.grid()
                    for plot_dict in plot:
                        if plot_dict['type'] == 'bool':
                            events = []
                            for day_num, day_index in enumerate(range(first_index, last_index)):
                                if plot_dict['field'] in self.database[day_index]:
                                    if self.database[day_index][plot_dict['field']]:
                                        events.append(day_num)
                            ax.eventplot(events, colors=plot_dict['color'], linelengths=20)
                        else:
                            values = []
                            for day_index in range(first_index, last_index):
                                if plot_dict['field'] in self.database[day_index]:
                                    values.append(self.database[day_index][plot_dict['field']])
                                else:
                                    values.append(-1)
                            ax.plot(values, '*-', color=plot_dict['color'])
                plt.show()

        except FileNotFoundError:
            print("Run config_plots.py")