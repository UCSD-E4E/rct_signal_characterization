#!/usr/bin/env python3

import os
import matplotlib.pyplot as plt; plt.ion()
import glob
import struct
import numpy as np

FFT_LEN = 2048
f_s = 2000000
fft_bin = 564
# 172.05 MHz
f_c = 172500000

if __name__ == '__main__':
	data_dir = "/media/ntlhui/FA56-CFCD/2017.08.19/RUN_000025/"
	raw_files = sorted(glob.glob(os.path.join(data_dir, 'RAW_DATA_*')))

	samples = []

	for raw_file in raw_files[7:8]:
		with open(raw_file, 'rb') as data_file:
			data = data_file.read()
		for i in range(int(len(data) / 4)):
			tsample = struct.unpack('hh', data[i * 4:(i+1) * 4])
			sample = (tsample[0] + tsample[1] * 1j) / 1024
			samples.append(sample)
		seq_samples = np.array(samples)
		arr_samples = np.reshape(seq_samples[0:FFT_LEN*int(len(samples) / FFT_LEN)], (FFT_LEN, int(len(samples) / FFT_LEN)), order='F')
		f_samp = np.fft.fft(arr_samples, axis=0) / FFT_LEN
		waterfall = np.power(np.abs(np.fft.fftshift(f_samp, axes=0)), 2)

		waterfall_extents = ((f_c - f_s / 2) / 1e6, (f_c + f_s / 2) / 1e6, len(seq_samples) / f_s, 0)

		freq_isolate = waterfall[fft_bin,:]

		t = np.arange(len(freq_isolate)) / (len(freq_isolate) - 1) * waterfall_extents[2]
		fig1 = plt.figure()
		plt.plot(t, freq_isolate)
		plt.ylabel('Power')
		plt.xlabel('Time (s)')
		plt.title('Ping Signal')
		plt.savefig('ping_signal.png')
		plt.close()