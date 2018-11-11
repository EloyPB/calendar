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

# TO DO
# plot all results of correlation in multiple figures if necessary
# correlate all things
# ignore days


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
        self.types = {}
        self.implicit_sources = {}
        self.implicit_keywords = {}

        for line in lines[1:]:
            words = line.split()
            self.fields.append(words[1])
            self.types[words[1]] = locate(words[0])
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

    def fill_fields(self, day):
        for field, field_type in zip(self.fields, self.types):
            if field not in self.implicit_keywords:
                while True:
                    value = input(field + ': ')
                    if value != '':
                        try:
                            day[field] = field_type(value)
                            break
                        except ValueError:
                            print("Expecting " + str(field_type))
                    else:
                        break

    def fill_implicit_fields(self, day):
        for field, keyword in self.implicit_keywords.items():
            if self.implicit_sources[field] in day:
                day[field] = keyword in day[self.implicit_sources[field]]
            else:
                day[field] = False

    @staticmethod
    def visual_aid():
        string = "            |---|---|---|---|---|---|---|---|---|---|\n"
        string += "            0   1   2   3   4   5   6   7   8   9   10\n"
        return string

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
            if int in self.types.values or float in self.types.values:
                print(self.visual_aid())

            day = {'date': str(processing_date)}
            self.fill_fields(day)
            self.fill_implicit_fields(day)
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
            if int in self.types.values or float in self.types.values:
                initial_string = self.visual_aid() + '\n'
                tf.write(bytes(initial_string, 'utf-8'))
            tf.write(bytes(day, 'utf-8'))
            tf.flush()
            editor = os.environ.get('EDITOR', 'vim')
            call([editor, tf.name])

            tf.seek(len(initial_string))
            edited_day = json.loads(tf.read())
            self.fill_implicit_fields(edited_day)
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

    def read_values(self, field, first_index, last_index, precision=1):
        mask = np.zeros(last_index-first_index)
        values = np.zeros(last_index-first_index)
        for day_num, day_index in enumerate(range(first_index, last_index)):
            day = self.database[day_index]
            if field in day:
                values[day_num] = round(day[field], precision)
            else:
                mask[day_num] = 1
        return np.array(values), np.array(mask)

    def list_to_bool(self, field, first_index, last_index, separator=', '):
        # get the list of elements and how many times each of them appears
        unsorted_list = []
        unsorted_counts = []
        for day_num, day_index in enumerate(range(first_index, last_index)):
            day = self.database[day_index]
            if field in day:
                for elem in day[field].split(separator):
                    if elem in unsorted_list:
                        unsorted_counts[unsorted_list.index(elem)] += 1
                    else:
                        unsorted_list.append(elem)
                        unsorted_counts.append(1)

        # sort factors by frequency
        sorted_counts = sorted(unsorted_counts, reverse=True)
        sorted_list = sorted(unsorted_list, reverse=True,
                             key=lambda e: unsorted_counts[unsorted_list.index(e)])

        # print sorted list
        for factor, count in zip(sorted_list, sorted_counts):
            print(count, factor)
        print('\n')

        # create matrix
        mat = np.zeros((last_index-first_index, len(sorted_list)))
        mask = np.zeros(last_index-first_index)
        for day_num, day_index in enumerate(range(first_index, last_index)):
            day = self.database[day_index]
            if field in day:
                day_list = day[field].split(separator)
                for elem_num, elem in enumerate(sorted_list):
                    if elem in day_list:
                        mat[day_num, elem_num] = 1
            else:
                mask[day_num] = 1
        return mat, mask, sorted_list

    @staticmethod
    def bool_to_intervals(values, mask):
        indices = []
        intervals = []
        intervals_mask = []
        found_stream = False
        for day_num, value in enumerate(values):
            if value and not found_stream:
                found_stream = True
                beginning = day_num
            elif found_stream and mask[day_num]:
                found_stream = False
                indices.append(day_num)
                intervals.append(0)
                intervals_mask.append(1)
            elif found_stream and value:
                indices.append(day_num)
                intervals.append(day_num - beginning)
                intervals_mask.append(0)
                beginning = day_num
        return indices, intervals, intervals_mask

    @staticmethod
    def moving_average(day_indices, values, mask, window):
        pass

    def plot(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("fields", help="fields to plot separated by commas (without spaces)")
        parser.add_argument("num_days", type=int, help="number of days to plot")
        parser.add_argument("-d", "--date", help="first date to plot")
        parser.add_argument("-a", "--average", type=int, help="width of the moving average in days")
        args = parser.parse_args()

        first_index, last_index = self.index_range(args.num_days, args.date)
        num_days = last_index - first_index

        # prepare dates for x tick labels
        first_date = datetime.strptime(self.database[first_index]['date'], "%Y-%m-%d").date()
        dates = [first_date + timedelta(days=n) for n in range(num_days)]

        fig, ax = plt.subplots()
        ax.set_ylim(0, 1)
        ax.set_yticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        ax.yaxis.grid()
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = prop_cycle.by_key()['color']

        if '.i' in args.fields:
            axr = ax.twinx()

        fields = args.fields.split(',')
        for plot_num, field in enumerate(fields):
            color = colors[plot_num % len(colors)]

            got_values = False
            is_bool = False
            for field_name in self.fields:
                if field_name in field and self.types[field_name] is str:
                    mat, mask, sorted_list = self.list_to_bool(field_name, first_index, last_index)
                    factor = field.split(':')[1].strip('.i').strip('.b')
                    column = sorted_list.index(factor)
                    values = mat[:, column]
                    got_values = True
                    is_bool = True
            if not got_values:
                stripped_field = field.strip('.i').strip('.b')
                values, mask = self.read_values(stripped_field, first_index, last_index)

            if '.i' in field:
                indices, values, mask = self.bool_to_intervals(values, mask)
                x = [dates[index] for index in indices]
                axr.plot(x, np.ma.masked_array(values, mask), '.-', label=field, color=color)
                axr.legend(loc='upper right')
            elif '.b' in field:
                ax.plot(dates, np.ma.masked_array(values, mask), '.-', label=field, color=color)
                ax.legend(loc='upper left')
            elif self.types[field.split(':')[0]] in (int, float):
                values = values/10
                ax.plot(dates, np.ma.masked_array(values, mask), '.-', label=field, color=color)
                ax.legend(loc='upper left')
            elif self.types[field.split(':')[0]] is bool or is_bool:
                events = []
                for day_num, value in enumerate(values):
                    if value:
                        day_index = day_num + first_index
                        events.append(datetime.strptime(self.database[day_index]['date'], "%Y-%m-%d").date())
                ax.eventplot(events, linelengths=20, label=field, color=color)
                ax.legend(loc='upper left')

        plt.show()

    def correlate(self):
        np.seterr(all='ignore')
        parser = argparse.ArgumentParser()
        parser.add_argument("factors_field", help="field containing lists of factors")
        parser.add_argument("values_field", help="field with values to correlate")
        parser.add_argument("-w", "--window", help="window size", default=5, type=int)
        args = parser.parse_args()

        factors_mat, factors_mask, factors_list = self.list_to_bool(args.factors_field, 0, len(self.database))
        values, values_mask = self.read_values(args.values_field, 0, len(self.database))

        # calculate correlations
        num_factors = len(factors_list)
        corr = np.zeros((num_factors, args.window))

        for time_shift in range(0, args.window):
            corrected_mat = []
            corrected_values = []
            for day_num, mask in enumerate(factors_mask):
                if mask == 0:
                    values_day_num = day_num + time_shift
                    if values_day_num < len(values) and values_mask[values_day_num] == 0:
                        corrected_mat.append(factors_mat[day_num])
                        corrected_values.append(values[values_day_num])
            corrected_mat = np.array(corrected_mat)
            for factor_num in range(num_factors):
                corr[factor_num, time_shift] = pearsonr(corrected_mat[:, factor_num], corrected_values)[0]

        # plot
        num_rows = 25
        num_cols = min(math.ceil(num_factors / num_rows), 5)
        corr = np.pad(corr, ((0, max(num_rows * num_cols - num_factors, 0)), (0, 0)), 'constant',
                            constant_values=np.nan)

        fig, ax = plt.subplots(1, num_cols)
        for col_num in range(num_cols):
            first_index = col_num * num_rows
            last_index = (col_num + 1) * num_rows
            ax[col_num].matshow(corr[first_index:last_index], vmin=-1, vmax=1)
            ax[col_num].set_yticks([i for i in range(num_rows)])
            ax[col_num].set_yticklabels(factors_list[first_index:last_index])

        plt.show()