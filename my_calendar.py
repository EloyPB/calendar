import json
from pydoc import locate
from datetime import date, datetime, timedelta
import calendar


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
        self.fields = []
        self.explicit_fields = []
        self.explicit_types = []
        self.implicit_fields = []

        for line in lines[1:]:
            words = line.split(', ')
            self.fields.append(words[0])
            if words[1] == 'implicit':
                self.implicit_fields.append({'field': words[0], 'source': words[2].split(':')[0],
                                             'key': words[2].split(':')[1]})
            else:
                self.explicit_fields.append(words[0])
                self.explicit_types.append(locate(words[1]))

        with open(self.path, 'r') as f:
            self.database = json.load(f)

    def dump(self):
        with open(self.path, 'w') as f:
            json.dump(self.database, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)

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
            for implicit_field in self.implicit_fields:
                day[implicit_field['field']] = implicit_field['key'] in day[implicit_field['source']]

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

    def display(self, num_days=None, first_date=None, last_date=None):
        print("\n")

        week_days = ["Monday    ", "Tuesday   ", "Wednesday ", "Thursday  ",
                     "Friday    ", "Saturday  ", "Sunday    "]

        if num_days is not None:
            first_index = -num_days
            last_index = 0
        else:
            first_index = self.date_to_index(first_date)
            if last_date is not None:
                last_index = self.date_to_index(last_date) + 1
            else:
                last_index = len(self.database)

        for day_index in range(first_index, last_index):
            day = self.database[day_index]
            processing_date = datetime.strptime(day['date'], "%Y-%m-%d").date()
            week_day = week_days[processing_date.weekday()]

            string = week_day + day['date'] + "  "
            for field in self.fields:
                if field in day:
                    value = day[field]
                    if type(value) is str:
                        string += '\n'
                    string += field + ': ' + str(value) + ' '

            print(string + '\n')

        print("\n")


