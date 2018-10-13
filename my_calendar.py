import os
import json
import calendar
import tempfile
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
        try:
            with open('config.txt') as f:
                lines = [line.rstrip('\n') for line in f]
        except FileNotFoundError:
            print("\nConfiguration file not found. \nPlease create a file named 'config.txt' in this directory."
                  "\nThe first line must contain the path to the file where the data will be saved, "
                  "including the desired file name with .json extension."
                  "\nIn subsequent lines declare the fields to be recorded. Each line must consist of a type "
                  "(int, float, bool, str) followed by a space and the name of the field. "
                  "\nIt is also possible to add implicit boolean fields "
                  "which will take a value of True if a keyword is mentioned in the string of another field. "
                  "\nFor implicit fields, the lines should look like: 'field_name implicit source_field:keyword'\n")
            exit()

        self.path = lines[0]
        self.explicit_fields = []
        self.explicit_types = []
        self.implicit_fields = []
        self.implicit_sources = []
        self.implicit_keys = []

        for line in lines[1:]:
            words = line.split()
            if words[0] == 'implicit':
                self.implicit_fields.append(words[1])
                self.implicit_sources.append(words[2].split(':')[0])
                self.implicit_keys.append(words[2].split(':')[1])
            else:
                self.explicit_types.append(locate(words[0]))
                self.explicit_fields.append(words[1])

        try:
            with open(self.path, 'r') as f:
                self.database = json.load(f)
        except FileNotFoundError:
            print('Database not found, creating a new one...')
            self.database = []
            self.dump()

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
        if len(self.database) > 0:
            last_date = datetime.strptime(self.database[-1]['date'], "%Y-%m-%d").date()
        else:
            last_date = date_today - timedelta(days=1)
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
        if first_date <= processing_date <= last_date:
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
        num_days = last_index - first_index

        # prepare dates for x tick labels
        first_date = datetime.strptime(self.database[first_index]['date'], "%Y-%m-%d").date()
        dates = [first_date + timedelta(days=n) for n in range(num_days)]

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
                                        events.append(datetime.strptime(self.database[day_index]['date'], "%Y-%m-%d").date())
                            ax.eventplot(events, colors=plot_dict['color'], linelengths=20)
                        else:
                            values = np.zeros(num_days)
                            for day_num, day_index in enumerate(range(first_index, last_index)):
                                if plot_dict['field'] in self.database[day_index]:
                                    values[day_num] = self.database[day_index][plot_dict['field']]
                                else:
                                    values[day_num] = -1
                            masked_values = np.ma.masked_where(values < 0, values)
                            ax.plot(dates, masked_values, '*-', color=plot_dict['color'])
                plt.show()

        except FileNotFoundError:
            print("Run config_plots.py")

    def events(self, field):
        num_days = len(self.database)

        count = -2
        times = []  # when the event is true
        intervals = []  # all of the intervals
        intervals_counts = []  # number of times the interval has occurred
        histogram = []  # sorted intervals with their number of occurrences
        years = []

        for n, day in enumerate(self.database):
            count += 1
            if day[field]:
                while count >= len(histogram):
                    histogram.append(0)
                if count > 0:
                    times.append(n)
                    intervals.append(count)
                    intervals_counts.append(histogram[count])
                    histogram[count] += 1
                count = 0
            if day['date'][5:] == '01-01':
                years.append((n, day['date'][:4]))

        print("\nCurrent count: {} days".format(count))
        higher_than = sum(histogram[:count])
        lower_than = sum(histogram[count + 1:])
        total = sum(histogram)
        print("Higher than ", round(higher_than / total * 100, 2), " and lower than ",
              round(lower_than / total * 100, 2))

        while True:
            option = input("\n(q)uit, (h)istogram, (p)ercentiles or (c)orrelation: ")

            if option == "q":
                exit()

            elif option == "h":
                colors = np.zeros((max(histogram), len(histogram)))

                for n, time in enumerate(times):
                    colors[intervals_counts[n], intervals[n]] = time / num_days
                masked_colors = np.ma.masked_equal(colors, 0)

                fig, ax = plt.subplots()
                pc = ax.pcolormesh(masked_colors)
                cbar = fig.colorbar(pc, ticks=np.linspace(years[0][0] / num_days, years[-1][0] / num_days, len(years)))
                cbar.ax.set_yticklabels([year[1] for year in years])
                plt.show(block=False)

            elif option == "p":
                while True:
                    try:
                        window_size = int(input("Enter the size of the sliding window in days: [365] ") or 365)
                        break
                    except ValueError:
                        print("Give me a number")

                times = np.array(times)
                intervals = np.array(intervals)
                percentiles = [0, 25, 50, 75, 100]
                p = np.zeros((len(percentiles), num_days - window_size))

                for start in range(0, num_days - window_size):
                    window = intervals[(times >= start) & (times <= start + window_size)]
                    for i, percentile in enumerate(percentiles):
                        p[i, start] = np.percentile(window, percentile)

                fig, ax = plt.subplots(1)
                ax.fill_between(range(p[0].size), p[0], p[4], facecolor='C7', alpha=0.2)
                ax.fill_between(range(p[0].size), p[1], p[3], facecolor='C7', alpha=0.4)
                ax.plot(p[4], 'C7', label='100%', alpha=0.4)
                ax.plot(p[3], 'C7', label='75%')
                ax.plot(p[2], 'k', label='50%')
                ax.plot(p[1], 'C7', label='25%')
                ax.plot(p[0], 'C7', label='0%', alpha=0.4)
                ax.legend()

                ticks = []
                labels = []
                for year in years:
                    if window_size / 2 < year[0] < num_days - window_size / 2:
                        ticks.append(year[0] - window_size / 2)
                        labels.append(year[1])

                ax.set_xticks(ticks)
                ax.set_xticklabels(labels)

                ax.set_title("Percentiles in a sliding window of " + str(window_size) + " days")
                plt.show(block=False)

            elif option == "c":
                correlated_field = input('Field to correlate: ')
                first_date = datetime.strptime(self.database[0]['date'], "%Y-%m-%d").date()
                start_date = datetime.strptime("2018-04-07", "%Y-%m-%d").date()
                start_index = (start_date - first_date).days

                found_pain = False
                index = -1
                while not found_pain:
                    if self.database[index]['pain']:
                        found_pain = True
                    else:
                        index -= 1
                end_index = len(self.database) + index

                periods = []
                new_period = []
                for day in self.database[start_index:end_index + 1]:
                    new_period.append(day[correlated_field])
                    if day['pain']:
                        periods.append(new_period)
                        new_period = []

                max_length = 0
                for period in periods:
                    if len(period) > max_length:
                        max_length = len(period)

                mat_normalized = np.zeros((len(periods), max_length))

                for period_num, period in enumerate(periods):
                    for i in range(max_length):
                        ii = i / (max_length - 1)
                        x = ii * (len(period) - 1)
                        mat_normalized[period_num, i] = period[round(x)]

                p25 = np.percentile(mat_normalized, 25, axis=0)
                p50 = np.percentile(mat_normalized, 50, axis=0)
                p75 = np.percentile(mat_normalized, 75, axis=0)

                x_axis = np.linspace(0, 1, max_length)

                fig, ax = plt.subplots()
                ax.fill_between(x_axis, p25, p75, alpha=0.4)
                ax.plot(x_axis, p25)
                ax.plot(x_axis, p50)
                ax.plot(x_axis, p75)

                mat = np.zeros((len(periods), max_length))
                mask = np.ones((len(periods), max_length))
                fig, ax = plt.subplots()
                for period_num, period in enumerate(periods):
                    ax.plot(period, color='gray', marker='.', linestyle='none')
                    for day_num, sat in enumerate(period):
                        mat[period_num, day_num] = sat
                        mask[period_num, day_num] = 0
                masked_array = np.ma.masked_array(mat, mask)
                average = np.mean(masked_array, axis=0)
                ax.plot(average, 'b')
                ax.set_ylim([0, 10])
                ax.grid()

                plt.show()