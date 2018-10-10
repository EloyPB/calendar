import json
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

sat = []

with open('/media/DATA/MEGA/Calendar.json', 'r') as f:
    dataArray = json.load(f)

    for day in dataArray:
        if 'sat' in day:
            sat.append(day['sat'])

x = np.array(sat) - np.mean(sat)
f, pxx_den = signal.welch(x, 1, nperseg=365)
plt.plot(f, pxx_den)
plt.show()

# fs = 10e3
# N = 1e5
# amp = 2*np.sqrt(2)
# freq = 1234.0
# noise_power = 0.001 * fs / 2
# time = np.arange(N) / fs
# x = amp*np.sin(2*np.pi*freq*time)
# x += np.random.normal(scale=np.sqrt(noise_power), size=time.shape)
#
# f, Pxx_den = signal.periodogram(x, fs)
# f_welch, Pxx_den_welch = signal.welch(x, fs, nperseg=1024)
# plt.semilogy(f, Pxx_den)
# plt.semilogy(f_welch, Pxx_den_welch, 'r')
# plt.ylim([1e-7, 1e2])
# plt.xlabel('frequency [Hz]')
# plt.ylabel('PSD [V**2/Hz]')
# plt.show()
