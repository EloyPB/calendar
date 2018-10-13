import json


with open('/media/DATA/MEGA/Calendar.json', 'r') as f:
    data_array = json.load(f)

    for day in data_array:
        if day['pain']:
            if 'text' in day:
                if 'PAIN,' not in day['text']:
                    day['text'] = 'PAIN, ' + day['text']
            else:
                day['text'] = 'PAIN, ...'


with open('/media/DATA/MEGA/calendar.json', 'w') as f:
    json.dump(data_array, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)