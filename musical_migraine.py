import json
import locale
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from datetime import datetime, timedelta


num_top_artists = 20
num_side_days = 10
num_shuffles = 2000


calendar_path = '/c/DATA/CLOUD/calendar.json'
scrobbles_path = '/c/DATA/CLOUD/Documentos/scrobbles.csv'


# load scrobbles
scrobbles = pd.read_csv(scrobbles_path)
locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
scrobbles.utc_time = pd.to_datetime(scrobbles.utc_time)
scrobbles = scrobbles[scrobbles.utc_time >= pd.Timestamp('2013-12-01')]
scrobbles['ord_date'] = scrobbles['utc_time'].dt.date.apply(lambda x: x.toordinal())
scrobbles = scrobbles.loc[:, ('utc_time', 'ord_date', 'artist')]
scrobbles = scrobbles.iloc[::-1].reset_index(drop=True)

artist_counts = scrobbles.artist.value_counts()
top_artists = artist_counts.head(num_top_artists).index.tolist()
scrobbles.loc[~scrobbles['artist'].isin(top_artists), 'artist'] = 'Other'

scrobble_ord_dates = scrobbles['ord_date'].to_numpy()

first_ord_date = scrobbles['ord_date'].iat[0]
last_ord_date = scrobbles['ord_date'].iat[-1]
num_days = last_ord_date - first_ord_date + 1


# load migraines
with open(calendar_path, 'r') as file:
    data = json.load(file)

pain_dates = [pd.Timestamp(entry['date']) for entry in data if entry.get('pain') == True]
pain_dates = [pain_date for pain_date in pain_dates if pain_date >= scrobbles['utc_time'].iat[0]]
pain_ord_dates = np.array([pain_date.toordinal() for pain_date in pain_dates])
pain_ord_dates = pain_ord_dates[(pain_ord_dates - num_side_days >= first_ord_date) & (pain_ord_dates + num_side_days <= last_ord_date)]
num_pains = len(pain_ord_dates)


# count top artist scrobbles in each day

artist_day_counts = np.zeros((num_days, num_top_artists))
total_day_counts = np.zeros(num_days)

start_idx = 0
for (day_num, ord_date) in enumerate(range(first_ord_date, last_ord_date+1)):
    left_idx = np.searchsorted(scrobble_ord_dates[start_idx:], ord_date, side='left')
    right_idx = np.searchsorted(scrobble_ord_dates[start_idx:], ord_date, side='right') - 1
    if right_idx > left_idx:
        left_idx += start_idx
        right_idx += start_idx
        start_idx = right_idx + 1
        
        day_scrobbles = scrobbles.iloc[left_idx:right_idx]
        day_counts = day_scrobbles['artist'].value_counts()
        
        for artist, count in day_counts.items():
            if artist != 'Other':
                artist_num = top_artists.index(artist)
                artist_day_counts[day_num, artist_num] = count
        
        total_day_counts[day_num] = day_scrobbles.shape[0]
        
        
# align to migraines
aligned_scrobbles = np.zeros((num_top_artists, num_side_days*2+1))
aligned_totals = np.zeros(num_side_days*2+1)

for pain_num in range(num_pains):
    ord_date_num = pain_ord_dates[pain_num] - first_ord_date
    
    for (offset_num, offset) in enumerate(range(-num_side_days, num_side_days+1)):
        aligned_scrobbles[:, offset_num] += artist_day_counts[ord_date_num+offset, :]
        aligned_totals[offset_num] += total_day_counts[ord_date_num+offset]
    
            
            
# aligned_fractions = aligned_scrobbles / aligned_totals
aligned_fractions = aligned_scrobbles


# shuffles 
rng = np.random.default_rng()
shuffled_fractions = np.empty((num_shuffles, num_top_artists))

pain_date_nums = np.array(pain_ord_dates) - first_ord_date
for shuffle_num in range(num_shuffles):
    random_idx = pain_date_nums + rng.integers(-num_side_days, num_side_days, size=num_pains)
    # shuffled_fractions[shuffle_num, :] = artist_day_counts[random_idx, :].sum(axis=0) / sum(total_day_counts[random_idx])
    shuffled_fractions[shuffle_num, :] = artist_day_counts[random_idx, :].sum(axis=0)
    

y1 = np.percentile(shuffled_fractions, 1, axis=0)
y99 = np.percentile(shuffled_fractions, 99, axis=0)
y5 = np.percentile(shuffled_fractions, 5, axis=0)
y95 = np.percentile(shuffled_fractions, 95, axis=0)

for artist_num in range(num_top_artists):
    fig, ax = plt.subplots()
    x = range(-num_side_days, num_side_days+1)
    ax.axvline(0, color='k', linestyle=':')
    ax.fill_between(x, y1[artist_num], y99[artist_num], color=np.array((179, 198, 255))/255, 
                    edgecolor='none', label='shuffled 99th percentile')
    ax.fill_between(x, y5[artist_num], y95[artist_num], color=np.array((128, 159, 255))/255, 
                    edgecolor='none', label='shuffled 95th percentile')
    ax.plot(x, aligned_fractions[artist_num, :], color='k')
    ax.set_title(top_artists[artist_num])
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend(loc='upper right')
    y_min, y_max = ax.get_ylim()
    ax.set_ylim((y_min, y_max*1.2))
    ax.set_ylabel('Scrobbles')
    ax.set_xlabel('Days from migraine')   
    artist_name = top_artists[artist_num].replace('/', '')
    fig.savefig(f'/home/eloy/Desktop/scrobbles/{artist_name}.png', dpi=300)