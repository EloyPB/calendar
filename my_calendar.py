import os
import json
import calendar
import argparse
import tempfile
import math
import numpy as np
import matplotlib.pyplot as plt
from pydoc import locate
from subprocess import call
from scipy.stats.stats import pearsonr
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
        self.fields = []
        self.types = []
        self.implicit_sources = {}
        self.implicit_keywords = {}

        for line in lines[1:]:
            words = line.split()
            self.types.append(locate(words[0]))
            self.fields.append(words[1])
            if len(words) > 2:
                self.implicit_sources[words[1]] = words[2].split(':')[0]
                self.implicit_keywords[words[1]] = words[2].split(':')[1]

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
        """Reorder database according to config file"""

        new_database = []
        for day in self.database:
            new_day = {'date': day['date']}
            for field in self.fields:
                if field in day:
                    new_day[field] = day[field]
            for field in day:
                if field not in self.fields:
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
            if int in self.types or float in self.types:
                print("            |---|---|---|---|---|---|---|---|---|---|")
                print("            0   1   2   3   4   5   6   7   8   9   10\n")

            day = {'date': str(processing_date)}
            for field, field_type in zip(self.fields, self.types):
                if field in self.implicit_keywords:
                    value = self.implicit_keywords[field] in day[self.implicit_sources[field]]
                else:
                    value = get_value(field, field_type)
                day[field] = value
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

    def edit(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--date", help="date to edit")
        args = parser.parse_args()

        if args.date is not None:
            edit_index = self.date_to_index(args.date)
        else:
            edit_index = -1

        day = json.dumps(self.database[edit_index], indent=4, separators=(',', ': '), ensure_ascii=False)

        with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
            if int in self.types or float in self.types:
                tf.write(bytes("            |---|---|---|---|---|---|---|---|---|---|\n", 'utf-8'))
                tf.write(bytes("            0   1   2   3   4   5   6   7   8   9   10\n\n", 'utf-8'))
            tf.write(bytes(day, 'utf-8'))
            tf.flush()
            editor = os.environ.get('EDITOR', 'vim')
            call([editor, tf.name])

            tf.seek(110)
            edited_day = json.loads(tf.read())
            self.database[edit_index] = edited_day

        self.dump()

    def index_range(self, num_days, first_date=None):
        if first_date is not None:
            first_index = self.date_to_index(first_date)
            last_index = min(first_index + num_days, len(self.database))
        else:
            first_index = -num_days
            last_index = 0
        return first_index, last_index

    def display(self):
        print("\n")

        parser = argparse.ArgumentParser()
        parser.add_argument("num_days", type=int, help="number of days to display")
        parser.add_argument("-d", "--date", help="first date to display")
        args = parser.parse_args()

        week_days = ["Monday    ", "Tuesday   ", "Wednesday ", "Thursday  ",
                     "Friday    ", "Saturday  ", "Sunday    "]

        brown = '\033[38;5;180m'
        blue = '\033[38;5;153m'
        reset = '\033[0m'

        first_index, last_index = self.index_range(args.num_days, args.date)

        for day_index in range(first_index, last_index):
            day = self.database[day_index]
            processing_date = datetime.strptime(day['date'], "%Y-%m-%d").date()
            week_day = week_days[processing_date.weekday()]

            string = week_day + day['date'] + "  "
            for field in self.fields:
                if field in day and field not in self.implicit_keywords:
                    value = day[field]
                    if type(value) is str:
                        # print strings in light brown, with implicit field keywords in light blue
                        string += '\n' + field + ': '
                        words = value.split()
                        for word in words:
                            if word in self.implicit_keywords.values():
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

    def plot(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("fields", help="fields to plot separated by commas (without spaces)")
        parser.add_argument("num_days", type=int, help="number of days to plot")
        parser.add_argument("-d", "--date", help="first date to plot")
        args = parser.parse_args()

        first_index, last_index = self.index_range(args.num_days, args.date)
        num_days = last_index - first_index

        # prepare dates for x tick labels
        first_date = datetime.strptime(self.database[first_index]['date'], "%Y-%m-%d").date()
        dates = [first_date + timedelta(days=n) for n in range(num_days)]

        fig, ax = plt.subplots()
        ax.set_ylim(0, 10)
        ax.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        ax.yaxis.grid()
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = prop_cycle.by_key()['color']

        fields = args.fields.split(',')
        for plot_num, field in enumerate(fields):
            field_num = self.fields.index(field)
            color = colors[plot_num % len(colors)]
            if self.types[field_num] is bool:
                events = []
                for day_num, day_index in enumerate(range(first_index, last_index)):
                    if field in self.database[day_index] and self.database[day_index][field] == True:
                        events.append(datetime.strptime(self.database[day_index]['date'], "%Y-%m-%d").date())
                ax.eventplot(events, linelengths=20, label=field, color=color)

            elif self.types[field_num] in (int, float):
                values = np.zeros(num_days)
                for day_num, day_index in enumerate(range(first_index, last_index)):
                    if field in self.database[day_index]:
                        values[day_num] = self.database[day_index][field]
                    else:
                        values[day_num] = -1
                masked_values = np.ma.masked_where(values < 0, values)
                ax.plot(dates, masked_values, '.-', label=field, color=color)
        ax.legend()
        plt.show()

    def correlate(self):
        np.seterr(all='ignore')

        parser = argparse.ArgumentParser()
        parser.add_argument("factors_field", help="field containing lists of factors")
        parser.add_argument("values_field", help="field with values to correlate")
        parser.add_argument("-w", "--window", help="window size", default=5, type=int)
        args = parser.parse_args()

        # find indices of the last uninterrupted stream of data
        found_stream = False
        for day_index in range(-1, -len(self.database)-1, -1):
            if not found_stream:
                if args.factors_field in self.database[day_index] and args.values_field in self.database[day_index]:
                    last_index = day_index
                    found_stream = True
            else:
                if (day_index == -len(self.database) or args.factors_field not in self.database[day_index]
                        or args.values_field not in self.database[day_index]):
                    first_index = day_index + 1
                    break

        # get the list of factors and how many times each of them appears
        unsorted_factor_list = []
        unsorted_factor_counts = []
        for day_index in range(first_index, last_index+1, 1):
            day = self.database[day_index]
            for factor in day[args.factors_field].split(', '):
                if factor in unsorted_factor_list:
                    unsorted_factor_counts[unsorted_factor_list.index(factor)] += 1
                else:
                    unsorted_factor_list.append(factor)
                    unsorted_factor_counts.append(1)

        num_days = -(first_index - last_index - 1)
        print('\nAnalysis based on %d days\n' % num_days)

        # sort factors by frequency
        factor_counts = sorted(unsorted_factor_counts, reverse=True)
        factor_list = sorted(unsorted_factor_list, reverse=True, key=lambda f: unsorted_factor_counts[unsorted_factor_list.index(f)])

        # print sorted list
        for factor, count in zip(factor_list, factor_counts):
            print(count, factor)
        print('\n')

        # create matrix
        num_factors = len(factor_list)
        mat = np.zeros((num_days, num_factors))
        values = np.zeros(num_days)

        for day_num, day_index in enumerate(range(first_index, last_index+1, 1)):
            day = self.database[day_index]
            values[day_num] = day[args.values_field]

            for factor_num, factor in enumerate(factor_list):
                if factor in day[args.factors_field].split(", "):
                    mat[day_num, factor_num] = 1

        # calculate correlations
        corr = np.zeros((num_factors, args.window))

        for factor_num in range(num_factors):
            for time_shift in range(0, args.window):
                corr[factor_num, time_shift] = pearsonr(mat[0:num_days - time_shift, factor_num], values[time_shift:])[0]

        # plot
        num_rows = 25
        num_cols = min(math.ceil(num_factors / num_rows), 5)
        sharp_corr = np.pad(corr, ((0, max(num_rows * num_cols - num_factors, 0)), (0, 0)), 'constant',
                            constant_values=np.nan)

        fig, ax = plt.subplots(1, num_cols)
        for col_num in range(num_cols):
            first_index = col_num * num_rows
            last_index = (col_num + 1) * num_rows
            ax[col_num].matshow(sharp_corr[first_index:last_index], vmin=-1, vmax=1)
            ax[col_num].set_yticks([i for i in range(num_rows)])
            ax[col_num].set_yticklabels(factor_list[first_index:last_index])

        plt.show()