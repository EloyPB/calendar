import json


with open('/media/DATA/MEGA/OldCalendar.json', 'r') as f:
    dataArray = json.load(f)

    keys = ["body", "mind", "no-p", "exp", "nota"]

    for day in dataArray:

        day["date"] = day["fecha"]
        del day["fecha"]

        for key in keys:
            if key in day and day[key] < 0:
                del day[key]

        if day["texto"] != "":
            day["text"] = day["texto"]
        del day["texto"]

        if "nota" in day:
            day["sat"] = day["nota"]
            del day["nota"]

        if "food" in day:
            day['nourr'] = day["food"]
            del day["food"]

with open('/media/DATA/MEGA/LeanCalendar.json', 'w') as f:
    json.dump(dataArray, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
