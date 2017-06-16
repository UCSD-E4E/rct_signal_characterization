
#templateFile = open('C:\\Users\\danny\\Documents\\ucsd\\CSE237D\\RCTSpring2017\\Collar_Emulator\\OnInput', 'rb')
signalFilename = 'C:\\Users\\danny\\Downloads\\recorded-complex.out'
# signalFilename = 'C:\\Users\\danny\\Downloads\\recorded-complex_1.out'
# signalFilename = 'C:\\Users\\danny\\Downloads\\recorded-complex_filtered_1.out'
signalFile = open(signalFilename, 'rb')

import struct

# Constants
SAMPLE_THRESH = 100 # min num of samples before counting rising edge
AMP_THRESH = 0.001 # amplitude threshold before considering a rising edge
SAMP_FREQ = 640000 # sampling frequency

print('Reading from ' + signalFilename)

amplitudes = []

for i in range(5120000):
    firstBytes = signalFile.read(4)
    secondBytes = signalFile.read(4)
    if (firstBytes == b'' or secondBytes == b''):
        break

    complexNum = complex(struct.unpack('f', firstBytes)[0], struct.unpack('f', secondBytes)[0])
    amplitudes.append( abs(complexNum) )

import numpy

def runningMeanFast(x, N):
    return numpy.convolve(x, numpy.ones((N,))/N, mode='valid')[-1]

counter = 0
risingIndex = -1
minNum = 1.0
prevElement = 0.0
for element in amplitudes:
    if prevElement < AMP_THRESH:
        if element > AMP_THRESH:
            risingIndex = counter

    if prevElement > AMP_THRESH:
        if element < AMP_THRESH:
            diff = counter - risingIndex
            if diff > SAMPLE_THRESH:
                print('rising edge: ' + str(risingIndex))
                print('falling edge: ' + str(counter))
                print('Difference=> ' + str(diff))
                print('Difference=> ' + str(diff / SAMP_FREQ * 1000) + "ms")
                print('Avg Amplitude=> ' + str(runningMeanFast(amplitudes[risingIndex:counter], diff)))

            # maybe not needed?
            risingIndex = -1

    if element < minNum and element != 0.0:
        minNum = element

    prevElement = element
    counter = counter + 1

tmpIndex = 0
for element in amplitudes:
    if element == 0.0:
        amplitudes[tmpIndex] = minNum
    tmpIndex = tmpIndex + 1


import matplotlib.pyplot as plt


amplitudes = 20*numpy.log10(amplitudes)
plt.plot(amplitudes)
plt.ylabel('amplitude (dBFS)')
plt.xlabel('samples (640k = 1s)')
plt.show()

#templateFile.close()
signalFile.close()
