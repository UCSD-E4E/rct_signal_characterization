#!/usr/bin/env python
# coding: utf-8

# In[1]:


import glob
import os
import numpy as np
import struct
import matplotlib.pyplot as plt; plt.ion()
import json
import pandas as pd

ping_width_ms=27
ping_min_snr=2000
ping_max_len_mult=1.5
ping_min_len_mult=0.5
frequencies=173965000
sampling_freq=1500000
center_freq = 173500000
FFT_LEN = 2048

target_freqs = np.array([173965000])
target_freqs = ((target_freqs - center_freq) / (sampling_freq / 2) * FFT_LEN /2).astype(np.int)


int_time_s = 6e-3
int_factor = int(int_time_s * sampling_freq / FFT_LEN)
clfr_input_freq = sampling_freq / int_factor / FFT_LEN
maximizer_len = int(0.1 * clfr_input_freq)
median_len = int(1 * clfr_input_freq)
ping_width_samp = ping_width_ms / 1000. * sampling_freq / FFT_LEN / int_factor
data_len = ping_width_samp * 2
id_len = clfr_input_freq * 0.5
_ms_per_sample = 1/(sampling_freq / int_factor / FFT_LEN) * 1e3


# In[2]:


files = sorted(glob.glob('**/RAW_DATA*', recursive=True))


# In[3]:


file = 'RUN_000481/RAW_DATA_000481_000004'
with open(file, 'rb') as datafile:
    fileContent = datafile.read()
fileSize = len(fileContent)
numSamples = int(fileSize / 4)
rawsamples = [struct.unpack('hh', fileContent[4*i:4*i+4]) for i in range(numSamples)]
samples = np.array([sample[0] + sample[1] * 1j for sample in rawsamples]) / np.iinfo(np.int16).max
fileTime = numSamples / sampling_freq


# In[4]:


run_num = int(os.path.split(file)[1].split('_')[2])
localizeFilePath = 'RUN_%06d/LOCALIZE_%06d' % (run_num, run_num)
metaFilePath = 'RUN_%06d/META_%06d' % (run_num, run_num)


# In[5]:


pings = []
with open(localizeFilePath) as localizeFile:
    for line in localizeFile:
        packet = json.loads(line)
        if 'ping' in packet:
            pings.append(packet['ping'])
start_time = 0;
with open(metaFilePath) as metaFile:
    for line in metaFile:
        if 'start_time' in line.split(': '):
            start_time = float(line.split(': ')[1].strip())


# In[6]:


fft_in = np.reshape(samples, (2048, int(numSamples / 2048)))
fft_out = np.fft.fft(fft_in, axis=0)


# In[7]:


df = pd.DataFrame(pings)
df['lat'] /= 1e7
df['lon'] /= 1e7
df['time'] /= 1e3
df['time'] -= start_time
df.iloc[0:5]


# In[8]:


shp = fft_out.shape
shp = shp[0], int(shp[1] / int_factor)
integrated_data = np.zeros(shp)
power_data = np.power(np.abs(fft_out), 2)
for i in range(shp[1]):
    integrated_data[:,i] = np.sum(power_data[:,int_factor * i:int_factor * (i + 1)])


# In[9]:


targetData = integrated_data[target_freqs[0],:]
peak_history = np.zeros(len(targetData) - maximizer_len)
for i in range(len(peak_history)):
    peak_history[i] = np.max(targetData[i:i+maximizer_len])
threshold = np.zeros(len(peak_history) - median_len)
for i in range(len(threshold)):
    threshold[i] = np.median(peak_history[i:i+median_len])
threshold = threshold + ping_min_snr


# In[16]:


plt.plot(np.arange(0, fileTime, fileTime / len(integrated_data)), 10 * np.log10(integrated_data[target_freqs[0],:]))
plt.plot(np.arange(0, fileTime, fileTime / len(threshold)), 10 * np.log10(threshold))
plt.savefig('test.png')


# In[11]:


peak_history.shape


# In[12]:


targetData.shape


# In[13]:


np.arange(0, fileTime, fileTime / len(integrated_data))


# In[14]:


len(integrated_data)


# In[15]:


run_num


# In[ ]:




