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


class Calendar:
    def __init__(self):
        """Reads the database path and fields from a configuration file and loads the database.
        """
        try:
            with open('config.txt') as f:
                lines = [line.rstrip('\n') for line in f]
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
                    with open(self.path, 'r', encoding='utf-8') as f:
                        self.database = json.load(f)
                except FileNotFoundError:
                    print('Database not found, creating a new one...')
                    self.database = []
                    self.dump()

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

    def dump(self):
        """Writes to the database file.
        """
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.database, f, indent=4, separators=(',', ': '), ensure_ascii=False)

    def reorder(self):
        """Reorders the database according to the configuration file.
        """
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
        """Asks the user to input values for the explicit fields and adds them to the day's dictionary.
        """
        for field in self.fields:
            if field not in self.implicit_keywords:
                while True:
                    value = input(field + ': ')
                    if value != '':
                        try:
                            day[field] = self.types[field](value)
                            break
                        except ValueError:
                            print("Expecting " + str(self.types[field]))
                    else:
                        break

    def fill_implicit_fields(self, day):
        """Checks for implicit fields and adds them to the day's dictionary.
        """
        for field, keyword in self.implicit_keywords.items():
            if self.implicit_sources[field] in day:
                day[field] = keyword in day[self.implicit_sources[field]]
            else:
                day[field] = False

    @staticmethod
    def visual_aid():
        """Creates the string that produces a scale from 0 to 10.
        """
        string = "            |---|---|---|---|---|---|---|---|---|---|\n"
        string += "            0   1   2   3   4   5   6   7   8   9   10\n"
        return string

    def add_days(self):
        """Fill in missing days in the database.
        """
        # find out current date, if it is before 20:00 the current day does not count
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--date", help="upper bound for the date")
        parser.add_argument("-s", "--skip", help="skip unfilled", action="store_true")
        args = parser.parse_args()

        if args.date is not None:
            end_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        else:
            end_date = date.today()
            if datetime.now().hour < 20:
                end_date -= timedelta(days=1)

        if args.skip or len(self.database) == 0:
            start_date = end_date - timedelta(days=1)
        else:
            start_date = datetime.strptime(self.database[-1]['date'], "%Y-%m-%d").date()

        days_missing = (end_date - start_date).days

        # get the information for each of the missing days
        if days_missing == 0:
            print("\nAlready up to date\n")
        else:
            for i in range(1, days_missing + 1):
                processing_date = start_date + timedelta(days=i)
                print("\nData for", calendar.day_name[processing_date.weekday()], processing_date, "\n")

                # if any of the fields expects a number, print a scale from 0 to 10 as a visual aid
                if int in self.types.values() or float in self.types.values():
                    print(self.visual_aid())

                day = {'date': str(processing_date)}
                self.fill_fields(day)
                self.fill_implicit_fields(day)
                self.database.append(day)

            self.dump()
            print("\n")

    def date_to_index(self, processing_date):
        """Finds the index of the database entry corresponding to some date.
        """
        first_date = datetime.strptime(self.database[0]['date'], "%Y-%m-%d").date()
        processing_date = datetime.strptime(processing_date, "%Y-%m-%d").date()
        last_date = datetime.strptime(self.database[-1]['date'], "%Y-%m-%d").date()
        if first_date <= processing_date <= last_date:
            return (processing_date - first_date).days
        else:
            print("Date out of range")

    def index_range(self, num_days, first_date=None):
        """Finds the first and last index corresponding to a period of num_days ending on the
        last date (default) or starting on first_date.
        """
        if first_date is None:
            first_index = max(0, len(self.database) - num_days)
        else:
            first_index = self.date_to_index(first_date)
        last_index = min(first_index + num_days, len(self.database))

        return first_index, last_index

    def edit(self):
        """Opens VIM to edit one database entry.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--date", help="date to edit")
        args = parser.parse_args()

        if args.date is not None:
            edit_index = self.date_to_index(args.date)
        else:
            edit_index = -1

        day = json.dumps(self.database[edit_index], indent=4, separators=(',', ': '), ensure_ascii=False)

        with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
            if int in self.types.values() or float in self.types.values():
                initial_string = self.visual_aid() + '\n'
                tf.write(bytes(initial_string, 'utf-8'))
            tf.write(bytes(day, 'utf-8'))
            tf.flush()
            editor = os.environ.get('EDITOR', 'vim')
            call([editor, tf.name])

            if int in self.types.values() or float in self.types.values():
                tf.seek(len(initial_string))
            edited_day = json.loads(tf.read())
            self.fill_implicit_fields(edited_day)
            self.database[edit_index] = edited_day

        self.dump()

    def display(self):
        """Displays on the terminal a period of num_days ending on the
        last date (default) or starting on first_date.
        """
        print("\n")

        parser = argparse.ArgumentParser()
        parser.add_argument("num_days", type=int, help="number of days to display")
        parser.add_argument("-d", "--date", help="first date to display")
        args = parser.parse_args()

        brown = '\033[38;5;180m'
        blue = '\033[38;5;153m'
        reset = '\033[0m'

        first_index, last_index = self.index_range(args.num_days, args.date)

        for day_index in range(first_index, last_index):
            day = self.database[day_index]
            processing_date = datetime.strptime(day['date'], "%Y-%m-%d").date()
            string = processing_date.strftime("%A %Y-%m-%d") + "  "
            for field in self.fields:
                if field in day and field not in self.implicit_keywords:
                    value = day[field]
                    if type(value) is str:
                        # print strings in light brown, with implicit field keywords in light blue
                        string += '\n' + field + ': '
                        indices_implicit = []
                        for implicit_keyword in self.implicit_keywords.values():
                            if implicit_keyword in value:
                                start = value.index(implicit_keyword)
                                end = start + len(implicit_keyword)
                                for index in range(start, end):
                                    indices_implicit.append(index)
                        for letter_index, letter in enumerate(value):
                            if letter_index in indices_implicit:
                                string += blue + letter + reset
                            else:
                                string += brown + letter + reset

                    elif type(value) is int or type(value) is float:
                        # print numbers following color gradient from 0:white to 10:green
                        rb = str(int((10 - value) * 25.5))
                        color = '\033[38;2;' + rb + ';255;' + rb + 'm'
                        string += field + ': ' + color + str(value) + reset + ' '

            print(string + '\n')
        print("\n")

    def read_values(self, field, first_index, last_index, precision=1):
        """Reads the values of one field from the database.
        """
        last_index = min(last_index, len(self.database))
        mask = np.zeros(last_index-first_index)
        values = np.zeros(last_index-first_index)
        for day_num, day_index in enumerate(range(first_index, last_index)):
            day = self.database[day_index]
            if field in day:
                values[day_num] = round(day[field], precision)
            else:
                mask[day_num] = 1
        return np.ma.masked_array(values, mask)

    @staticmethod
    def intervals(values):
        """Calculates the time intervals between occurrences of a boolean variable.
        """
        intervals = []
        intervals_mask = []
        beginning = 0
        stream_found = False
        for day_num, value in enumerate(values):
            if stream_found and value:
                intervals.append(day_num - beginning)
                intervals_mask.append(0)
                beginning = day_num
            else:
                intervals.append(0)
                intervals_mask.append(1)
                if value:
                    stream_found = True
                    beginning = day_num
                elif stream_found and values.mask[day_num]:
                    stream_found = False
        return np.ma.masked_array(intervals, intervals_mask)

    def list_to_bool(self, field, first_index, last_index, separator=', '):
        """Transforms a field consisting on lists of items into a matrix of days x items.
        """
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
    def moving_average(values, window_size):
        """Calculates a moving average over a window of size window_size.
        """
        averaged = np.ma.masked_array(np.zeros(len(values)), np.zeros(len(values)))
        averaged.mask[0:window_size-1] = True
        for day_index in range(window_size-1, len(values)):
            averaged[day_index] = np.mean(values[day_index-window_size+1:day_index])
        return averaged

    def get_values(self, complex_fields, first_index, last_index, averaging_window=0):
        values = []
        first_date = datetime.strptime(self.database[first_index]['date'], "%Y-%m-%d").date()
        dates = [first_date + timedelta(days=n) for n in range(last_index - first_index)]

        for complex_field in complex_fields:
            field = complex_field.split(':')[0].split('.')[0]
            if ':' in complex_field:
                mat, mask, sorted_list = self.list_to_bool(complex_field.split(':')[0], first_index, last_index)
                factor = complex_field.split(':')[1].split('.')[0]
                values_read = np.ma.masked_array(mat[:, sorted_list.index(factor)], mask)
            else:
                values_read = self.read_values(field, first_index, last_index)
                if self.types[field] in (int, float):
                    values_read /= 10

            if '.i' in complex_field:
                values_read = self.intervals(values_read)

            if averaging_window and ('.b' in complex_field or '.i' in complex_field
                                     or self.types[field] in (int, float)):
                values_read = self.moving_average(values_read, averaging_window)
            values.append(values_read)

        return dates, values

    def plot(self):
        """Plotting function.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("fields", help="fields to plot separated by commas (without spaces)")
        parser.add_argument("num_days", type=int, help="number of days to plot")
        parser.add_argument("-d", "--date", help="first date to plot")
        parser.add_argument("-a", "--average", type=int, help="window size in days")
        args = parser.parse_args()

        first_index, last_index = self.index_range(args.num_days, args.date)

        fig, ax = plt.subplots()
        ax.set_ylim(0, 1)
        ax.set_yticks(np.linspace(0, 1, 11))
        ax.yaxis.grid()
        axr = ax.twinx()
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = prop_cycle.by_key()['color']

        complex_fields = args.fields.split(',')
        dates, values = self.get_values(complex_fields, first_index, last_index, args.average)
        for plot_num, (complex_field, values) in enumerate(zip(complex_fields, values)):
            color = colors[plot_num % len(colors)]
            field = complex_field.split(':')[0].split('.')[0]

            # plot normal values
            if '.b' in complex_field in complex_field or self.types[field] in (int, float):
                ax.plot(dates, values, label=complex_field, color=color, marker='.')
                ax.legend(loc='upper left')

            # plot intervals on a new axis
            elif '.i' in complex_field:
                axr.plot(np.array(dates)[~values.mask], values[~values.mask], label=complex_field,
                         color=color, marker='.')
                axr.legend(loc='upper right')

            # plot events
            elif ':' in complex_field or self.types[field] is bool:
                events = []
                for day_num, value in enumerate(values):
                    if value:
                        day_index = day_num + first_index
                        events.append(datetime.strptime(self.database[day_index]['date'], "%Y-%m-%d").date())
                ax.eventplot(events, linelengths=20, label=complex_field, color=color)
                ax.legend(loc='upper left')

        plt.show()

    def histogram(self):
        """Plots a histogram.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("field", help="fields to plot separated by commas (without spaces)")
        parser.add_argument("-n", "--num_days", type=int, help="number of days to plot")
        parser.add_argument("-d", "--date", help="first date to plot")
        args = parser.parse_args()

        first_index, last_index = self.index_range(args.num_days, args.date)

        _, values = self.get_values([args.field], first_index, last_index)
        values = values[0]

    def percentiles(self):
        pass

    def cut(self):
        pass

    def correlate(self):
        """Correlates boolean variables contained in lists in factors_field with a multivalued variable."""
        np.seterr(all='ignore')
        parser = argparse.ArgumentParser()
        parser.add_argument("factors_field", help="field containing lists of factors")
        parser.add_argument("values_field", help="field with values to correlate")
        parser.add_argument("-w", "--window", help="window size", default=5, type=int)
        args = parser.parse_args()

        factors_mat, factors_mask, factors_list = self.list_to_bool(args.factors_field, 0, len(self.database))
        values = self.read_values(args.values_field, 0, len(self.database))

        # calculate correlations
        num_factors = len(factors_list)
        corr = np.zeros((num_factors, args.window))

        for time_shift in range(0, args.window):
            corrected_mat = []
            corrected_values = []
            for day_num, mask in enumerate(factors_mask):
                if mask == 0:
                    values_day_num = day_num + time_shift
                    if values_day_num < len(values) and values.mask[values_day_num] == 0:
                        corrected_mat.append(factors_mat[day_num])
                        corrected_values.append(values[values_day_num])
            corrected_mat = np.array(corrected_mat)
            for factor_num in range(num_factors):
                corr[factor_num, time_shift] = pearsonr(corrected_mat[:, factor_num], corrected_values)[0]

        # plot
        num_rows = 25
        num_cols = int(min(math.ceil(num_factors / num_rows), 5))
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

