import ephem
import matplotlib.pyplot as plt
import numpy as np
import math
import os
import glob
import thread
import time

samp_rate = 92.16e6
fftSize = 8192
bandwidth = samp_rate
c_freq = 2220e6

print os.path.dirname(__file__)

sky = np.load('/home/x310/Documents/sky.npy')
hot = np.load('/home/x310/Documents/hot.npy')

hdifsky = np.subtract(hot, sky)
speca = np.divide(spec, hdifsky)

spec = np.load('/home/x310/srFin.npy')


freq_res = bandwidth/fftSize # Hz
# List known RFI as center-frequency in MHz, and width in hz
known_RFI = [c_freq, 0.05]

RFI_freq = known_RFI[0]
RFI_width = known_RFI[1]*1e6
ch0_freq = c_freq - 0.5*bandwidth
ind_low = int(np.floor((RFI_freq-0.5*RFI_width - ch0_freq)/freq_res))
ind_high = int(np.ceil((RFI_freq+0.5*RFI_width - ch0_freq)/freq_res))
      
margin = min(ind_high-ind_low, ind_low, fftSize-ind_high)
RFI_part = spec[ind_low-margin:ind_high+margin]
xdata = np.arange(len(RFI_part))
weights = np.ones_like(RFI_part)
weights[margin:-margin] = 0.0 # Ignore RFI when fitting
pf = np.polyfit(xdata, RFI_part, deg=1, w=weights)
interpdata = np.polyval(pf, xdata)
		
spec[ind_low:ind_high] = interpdata[margin:-margin]

halffft = int(0.5*fftSize)
freqs = 0.5*samp_rate*np.array(range(-halffft,halffft))/(halffft)
freqs = np.array(range(fftSize))
plt.figure()
plt.title("Spectrum")
plt.plot(freqs, spec, '-')
plt.xlabel('[Hz]')
plt.ylabel('A')
plt.show()

t_hot = 273.15+24
t_cold = 77
b = np.subtract(hot_spectrum, cold_spectrum)
a = np.divide(cold_spectrum, b)
t_rec = a*(t_hot-t_cold)-t_cold

