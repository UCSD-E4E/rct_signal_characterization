
#templateFile = open('C:\\Users\\danny\\Documents\\ucsd\\CSE237D\\RCTSpring2017\\Collar_Emulator\\OnInput', 'rb')
signalFilename = 'C:\\Users\\danny\\Downloads\\recorded-complex.out'
signalFile = open(signalFilename, 'rb')

import struct

print('Reading from ' + signalFilename)

amplitudes = []

for i in range(20480000):
    firstBytes = signalFile.read(4)
    secondBytes = signalFile.read(4)
    if (firstBytes == b'' or secondBytes == b''):
        break

    complexNum = complex(struct.unpack('f', firstBytes)[0], struct.unpack('f', secondBytes)[0])
    amplitudes.append( abs(complexNum) )

import numpy

def runningMeanFast(x, N):
    return numpy.convolve(x, numpy.ones((N,))/N, mode='valid')[-1]

SAMPLE_THRESH = 100
counter = 0
risingIndex = -1
prevElement = 0.0
for element in amplitudes:
    if prevElement < 0.001:
        if element > 0.001:
            risingIndex = counter

    if prevElement > 0.001:
        if element < 0.001:
            diff = counter - risingIndex
            if diff > SAMPLE_THRESH:
                print('rising edge: ' + str(counter))
                print('falling edge: ' + str(counter))
                print('Difference=> ' + str(diff))
                print('Avg Amplitude=> ' + str(runningMeanFast(amplitudes[risingIndex:counter], diff)))

            # maybe not needed?
            risingIndex = -1

    prevElement = element
    counter = counter + 1


import matplotlib.pyplot as plt

plt.plot(amplitudes)
plt.ylabel('amplitudes')
plt.show()

#templateFile.close()
signalFile.close()
