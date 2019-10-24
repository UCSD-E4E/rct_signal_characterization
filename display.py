#!/usr/bin/env python3
import matplotlib.pyplot as plt; plt.ion()
import struct
import numpy as np
import os
import sys

FFT_LEN = 2048
IMG_HEIGHT = 2048

def displayProgress(count, total):
	percentComplete = float(count) / total
	DISPLAY_LEN = 50
	ZERO_CHAR = ' '
	COMPLETE_CHAR = '-'
	numChars = int(DISPLAY_LEN * percentComplete)
	sys.stdout.write('|')
	for i in range(numChars):
		sys.stdout.write(COMPLETE_CHAR)
	for i in range(DISPLAY_LEN - numChars):
		sys.stdout.write(ZERO_CHAR)
	sys.stdout.write('| %d%%, %d of %d\r' % (percentComplete * 100, count, total))

def main():
	inputSize = os.path.getsize('processedOutput')
	nRows = int(inputSize / (FFT_LEN * 4))
	img = np.zeros((nRows, FFT_LEN))
	with open('processedOutput', 'rb') as dataFile:
		for rowIdx in range(nRows):
			data = dataFile.read(FFT_LEN * 2 * 2)
			unpack = struct.unpack('hh' * FFT_LEN, data)
			for i in range(FFT_LEN):
				img[rowIdx, i] = abs((unpack[2 * i] + unpack[2 * i + 1] * 1j)) ** 2
			displayProgress(rowIdx, nRows)
	print('')
	img *= 255 / np.max(img)
	img = np.fft.fftshift(img, axes=1)
	print(np.max(img))
	for i in range(int(nRows / IMG_HEIGHT)):
		displayProgress(i, int(nRows / IMG_HEIGHT))
		plt.imsave('photos/final%02d.png' % (i + 1), img[IMG_HEIGHT * i:IMG_HEIGHT * (i + 1),:], vmin=0, vmax=255)
		displayProgress(i + 1, int(nRows / IMG_HEIGHT))
	print('')

if __name__ == '__main__':
	main()