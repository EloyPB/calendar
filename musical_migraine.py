import json
import locale
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


calendar_path = '/c/DATA/CLOUD/calendar.json'
scrobbles_path = '/c/DATA/CLOUD/Documentos/scrobbles.csv'

num_top_artists = 20
num_time_bins = 12
num_side_days = 10


scrobbles = pd.read_csv(scrobbles_path)
locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
scrobbles.utc_time = pd.to_datetime(scrobbles.utc_time)
scrobbles = scrobbles[scrobbles.utc_time >= pd.Timestamp('2013-12-01')]
scrobbles['ord_date'] = scrobbles['utc_time'].dt.date.apply(lambda x: x.toordinal())
scrobbles = scrobbles.loc[:, ('utc_time', 'ord_date', 'artist')]
scrobbles = scrobbles.iloc[::-1].reset_index(drop=True)


with open(calendar_path, 'r') as file:
    data = json.load(file)

pain_dates = [pd.Timestamp(entry['date']) for entry in data if entry.get('pain') == True]
pain_dates = [pain_date for pain_date in pain_dates if pain_date >= scrobbles['utc_time'].iat[0]]
pain_ord_dates = [pain_date.toordinal() for pain_date in pain_dates]

artist_counts = scrobbles.artist.value_counts()
top_artists = artist_counts.head(num_top_artists).index.tolist()


aligned_scrobbles = np.zeros((num_top_artists, num_side_days*2+1))
aligned_totals = np.zeros(num_side_days*2+1)


for pain_num in range(len(pain_dates) - 1):
    print(f'{pain_num}/{len(pain_dates)}')
    for (offset_num, offset) in enumerate(range(-num_side_days, num_side_days+1)):
        ord_date = pain_ord_dates[pain_num] + offset
        first_idx = scrobbles['ord_date'].searchsorted(ord_date, side='left')
        last_idx = scrobbles['ord_date'].searchsorted(ord_date, side='right') - 1
        date_scrobbles = scrobbles.iloc[first_idx:last_idx]
        if not date_scrobbles.empty:
            for (artist_num, artist) in enumerate(top_artists):
                aligned_scrobbles[artist_num, offset+num_side_days] += (date_scrobbles['artist'] == artist).sum()
            aligned_totals[offset+num_side_days] += date_scrobbles.shape[0]
            
            
aligned_fractions = aligned_scrobbles / aligned_totals


for artist_num in range(20):
    plt.figure()
    plt.plot(range(-num_side_days, num_side_days+1), aligned_fractions[artist_num, :])
    plt.axvline(0)
    plt.title(top_artists[artist_num])

        
    

# aligned_scrobbles = np.zeros((num_top_artists, num_time_bins))
# aligned_totals = np.zeros(num_time_bins)

# for pain_num in range(len(pain_dates) - 1):
#     period_start = pain_dates[pain_num] + timedelta(days=1)
#     period_end = pain_dates[pain_num + 1]
    
#     period_duration = period_end - period_start + timedelta(days=1)
    
#     bin_size = (period_duration) / num_time_bins
    
#     bin_start = period_start
#     for bin_num in range(num_time_bins):
#         bin_end = bin_start + bin_size
        
#         bin_scrobbles = scrobbles[(bin_start <= scrobbles['utc_time']) & (scrobbles['utc_time'] < bin_end)]
        
#         for (artist_num, artist) in enumerate(top_artists):
#             aligned_scrobbles[artist_num, bin_num] += (bin_scrobbles['artist'] == artist).sum()
            
#         aligned_totals[bin_num] += bin_scrobbles.shape[0]
            
#         bin_start = bin_end

    
# aligned_scrobbles = aligned_scrobbles / aligned_totals

# for artist_num in range(4):
#     plt.plot(aligned_scrobbles[artist_num, :], label=top_artists[artist_num])
# plt.legend()
