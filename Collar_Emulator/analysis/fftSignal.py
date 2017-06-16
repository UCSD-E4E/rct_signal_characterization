
# templateFilename = 'C:\\Users\\danny\\Documents\\ucsd\\CSE237D\\RCTSpring2017\\Collar_Emulator\\OnInput'
# templateFile = open(templateFilename, 'rb')
# signalFilename = 'C:\\Users\\danny\\Downloads\\recorded-complex.out'
# signalFilename = 'C:\\Users\\danny\\Downloads\\recorded-complex_1.out'
signalFilename = 'C:\\Users\danny\\Documents\\ucsd\\CSE237D\\RCTSpring2017\\Collar_Emulator\\snr_testing\\recv_100cm.data'
# signalFilename = 'C:\\Users\danny\\Documents\\ucsd\\CSE237D\\RCTSpring2017\\Collar_Emulator\\snr_testing\\recv_10cm.data'

signalFile = open(signalFilename, 'rb')

import struct
from datetime import datetime

print('Reading from ' + signalFilename)
print( str(datetime.now()) )

amplitudes = []

for i in range(1280000):
    firstBytes = signalFile.read(4)
    secondBytes = signalFile.read(4)
    if (firstBytes == b'' or secondBytes == b''):
        break

    complexNum = complex(struct.unpack('f', firstBytes)[0], struct.unpack('f', secondBytes)[0])
    amplitudes.append( complexNum )


# print('Reading from ' + templateFilename)
# print( str(datetime.now()) )
#
# amplitudes_template = []
#
# # TODO remove after messing with OnInput
# for i in range(6400):
#     amplitudes_template.append(0.0)
#
# for i in range(20480000):
#     firstBytes = templateFile.read(4)
#     secondBytes = templateFile.read(4)
#     if (firstBytes == b'' or secondBytes == b''):
#         break
#
#     complexNum = complex(struct.unpack('f', firstBytes)[0], struct.unpack('f', secondBytes)[0])
#     amplitudes_template.append( abs(complexNum) )
#
# # TODO remove after messing with OnInput
# for i in range(6400):
#     amplitudes_template.append(0.0)

import numpy as np

print('Computing fft of signal')
print( str(datetime.now()) )

# fft_output = numpy.fft.fft(amplitudes)

################ from https://kevinsprojects.wordpress.com/2014/12/13/short-time-fourier-transform-using-python-and-numpy/
# data = a numpy array containing the signal to be processed
# fs = a scalar which is the sampling frequency of the data

data = amplitudes
# fs = 640000
# overlap_fac = 0.5
# fft_size = 6400
fs = 32000
overlap_fac = 0.5
fft_size = 320

hop_size = np.int32(np.floor(fft_size * (1-overlap_fac)))
pad_end_size = fft_size          # the last segment can overlap the end of the data array by no more than one window size
total_segments = np.int32(np.ceil(len(data) / np.float32(hop_size)))
t_max = len(data) / np.float32(fs)

window = np.hanning(fft_size)  # our half cosine window
inner_pad = np.zeros(fft_size) # the zeros which will be used to double each segment size

proc = np.concatenate((data, np.zeros(pad_end_size)))              # the data to process
result = np.empty((total_segments, fft_size), dtype=np.float32)    # space to hold the result

for i in range(total_segments):                      # for each segment
    current_hop = hop_size * i                        # figure out the current segment offset
    segment = proc[current_hop:current_hop+fft_size]  # get the current segment
    windowed = segment * window                       # multiply by the half cosine function
    padded = np.append(windowed, inner_pad)           # add 0s to double the length of the data
    spectrum = np.fft.fft(padded) / fft_size          # take the Fourier Transform and scale by the number of samples
    autopower = np.abs(spectrum * np.conj(spectrum))  # find the autopower spectrum
    result[i, :] = autopower[:fft_size]               # append to the results array

# result = 20*np.log10(result)          # scale to db
# result = np.clip(result, -220, -190)    # clip values

fft_output = result
################# end copied and partially modified code

print('Done with fft')
print( str(datetime.now()) )


import matplotlib.pyplot as plt

# img = plt.imshow(result, origin='lower', cmap='jet', interpolation='nearest', aspect='auto')
# plt.show()
print(len(fft_output))
print(len(fft_output[0]))

for i in range(len(fft_output)):
    # if i == 100:
    #     plt.plot(fft_output[i][0:256])
    plt.plot(fft_output[i][0:256])
    # for j in range(len(fft_output[0])):
    #     if fft_output[i][j] > 2.5e-10:
    #         print('%d, %d: %d' % (i, j, fft_output[i][j]))

# plt.plot(fft_output)
plt.ylabel('Magnitude (dBFS)')
plt.xlabel('Frequency bins (50 Hz)')
plt.show()

#templateFile.close()
signalFile.close()
