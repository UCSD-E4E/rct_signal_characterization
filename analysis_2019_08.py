#!/usr/bin/env python3

import glob
import os
import datetime
import json
import multiprocessing
import numpy as np
import struct
from circular_buffer import CircularBuffer

import matplotlib.pyplot as plt; plt.ion()
import matplotlib.patches as patches

import pyfftw

FFT_LEN = 2048

CHANNEL_MAP = {	1:	172.951,
				2:	172.051,
				3:	172.012,
				4:	172.031,
				5:	172.112,
				6:	172.13,
				7:	172.192,
				8:	172.271,
				9:	172.411,
				10:	172.332,
				11:	172.911,
				12:	172.23,
				13:	172.071,
				14:	172.292,
				15:	172.252,
				16:	172.351,
				17:	172.17,
				18:	172.432,
				19:	172.492,
				20:	172.532,
				23:	172.691,
				24:	172.731}

class Ping:
	def __init__(self, time_ms, amplitude, freq, idx = 0, width_s=0):
		self.time_ms = time_ms
		self.amplitude = amplitude
		self.freq = freq
		self.idx = idx
		self.width_s = width_s

class RCTRun:
	"""RCT Run Information"""
	def __init__(self, path):
		self._path = path
		self._hasJson = os.path.isfile(os.path.join(self._path, 'run.json'))
		meta_candidates = glob.glob(os.path.join(self._path, 'META_*'))
		assert(len(meta_candidates) == 1)
		self._meta_path = meta_candidates[0]
		self._run_num = int(os.path.basename(meta_candidates[0]).split('_')[1])
		self._loaded_meta = False
		self._params = {}
		self._hasLocalize = os.path.isfile(os.path.join(self._path, 'LOCALIZE_%06d' % (self._run_num)))
		self._hasCol = os.path.isfile(os.path.join(self._path, 'COL'))
		self._hasColj = os.path.isfile(os.path.join(self._path, 'COLJ'))
		self._hasNotes = os.path.isfile(os.path.join(self._path, 'Notes'))
		self._hasDailyCSV = len(glob.glob(os.path.join(os.path.dirname(self._path), "*.csv"))) == 1
		self._hasDailyTXT = len(glob.glob(os.path.join(os.path.dirname(self._path), "*.txt"))) == 1
		self.tx_freq_set = set()
		self._pingWidth_ms = None
		self._minimumSNR = None
		self._maximumPingFactor = None
		self._minimumPingFactor = None
		self._dataScalar = 4096
		self._sampleWidth = 0
		if self._hasJson:
			self.loadJson()
		if self._hasLocalize:
			if os.path.getsize(os.path.join(self._path, 'LOCALIZE_%06d' % (self._run_num))) > 3:
				self._hasLocalizeData = True

	def setDataScalar(self, scalar):
		self._dataScalar = scalar

	def getDataScalar(self):
		return self._dataScalar

	def setMinSNR(self, snr):
		self._minimumSNR = float(snr)

	def getMinSNR(self):
		return self._minimumSNR

	def setPingFactor(self, factor):
		assert(isinstance(factor, tuple))
		assert(len(factor) == 2)
		assert(factor[1] > factor[0])
		self._maximumPingFactor = factor[1]
		self._minimumPingFactor = factor[0]

	def getPingFactor(self):
		return (self._minimumPingFactor, self._maximumPingFactor)

	def setPingWidth(self, width):
		assert(width > 0)
		self._pingWidth_ms = width

	def getPingWidth(self):
		return self._pingWidth_ms

	def setSampleWidth(self, width):
		assert(width > 0)
		self._sampleWidth = width

	def getSampleWidth(self):
		return self._sampleWidth

	def writeJson(self):
		packet = {}
		packet['run_num'] = self._run_num
		if not self._loaded_meta:
			self._load_meta()
		packet['start_time'] = self.getStartTime_ms()
		packet['center_freq'] = self.getCenterFreq()
		packet['sampling_freq'] = self.getSamplingFreq()
		packet['gain'] = self.getGain()
		packet['hasLocalize'] = self._hasLocalize
		packet['tx_freq'] = list(self.tx_freq_set)
		packet['minSNR'] = self._minimumSNR
		packet['minPingFactor'] = self._minimumPingFactor
		packet['maxPingFactor'] = self._maximumPingFactor
		packet['pingWidth_ms'] = self._pingWidth_ms
		packet['dataScalar'] = self._dataScalar
		packet['sampleWidth'] = self._sampleWidth
		with open(os.path.join(self._path, 'run.json'), 'w') as jsonFile:
			json.dump(packet, jsonFile)
			jsonFile.write('\n')

		self._hasJson = True

	def hasLocalize(self):
		return self._hasLocalize

	def loadJson(self):
		assert(self._hasJson)
		with open(os.path.join(self._path, 'run.json')) as jsonFile:
			packet = json.load(jsonFile)
		self._params['center_freq'] = packet['center_freq']
		self._params['sampling_freq'] = packet['sampling_freq']
		self._params['start_time'] = packet['start_time']
		self._params['gain'] = packet['gain']
		self._minimumSNR = packet['minSNR']
		self._minimumPingFactor = packet['minPingFactor']
		self._maximumPingFactor = packet['maxPingFactor']
		self._pingWidth_ms = packet['pingWidth_ms']
		try:
			self._sampleWidth = packet['sampleWidth']
		except KeyError as e:
			self._sampleWidth = 2
		try:
			self._dataScalar = packet['dataScalar']
		except KeyError as e:
			self._dataScalar = 4096
		tx_freqs = packet['tx_freq']
		self.tx_freq_set = set()
		for freq in tx_freqs:
			if isinstance(freq, int):
				self.tx_freq_set.add(freq)

	def _split_tag(self, line):
		split = line.split(':')
		key = split[0].strip()
		value = split[1].strip()
		return (key, value)

	def _load_meta(self):
		with open(self._meta_path) as meta_file:
			for line in meta_file:
				key, value = self._split_tag(line)
				self._params[key] = value

		self._loaded_meta = True

	def _getKey(self, key):
		if self._hasJson:
			pass
		elif not self._loaded_meta:
			self._load_meta()
		assert(key in self._params)
		return self._params[key]

	def getStartTime_ms(self):
		return float(self._getKey('start_time'))

	def getStartTime(self):
		return datetime.datetime.fromtimestamp(self._getKey('start_time'))

	def getCenterFreq(self):
		return int(self._getKey('center_freq'))

	def getSamplingFreq(self):
		return int(self._getKey('sampling_freq'))

	def getGain(self):
		return float(self._getKey('gain'))

	def getPath(self):
		return self._path

	def getRunNum(self):
		return self._run_num

	def getDataFiles(self):
		return glob.glob(os.path.join(self._path, 'RAW_DATA_*'))

	def getGPSFile(self):
		return glob.glob(os.path.join(self._path, 'GPS_*'))

	def getLocalizeFile(self):
		return glob.glob(os.path.join(self._path, 'LOCALIZE_*'))

	def hasCol(self):
		return self._hasCol

	def hasColj(self):
		return self._hasColj

	def loadCol(self):
		with open(os.path.join(self._path, 'COL')) as colFile:
			for line in colFile:
				txNum, freq = self._split_tag(line)
				self.tx_freq_set.add(int(freq))

	def hasNotes(self):
		return self._hasNotes

	def loadColj(self):
		with open(os.path.join(self._path, 'COLJ')) as colFile:
			cols = json.load(colFile)
		freqs = [int(CHANNEL_MAP[int(col)] * 1e6) for col in cols]
		[self.tx_freq_set.add(freq) for freq in freqs]

	def getFreqs(self):
		return list(self.tx_freq_set)

	def loadNotes(self):
		colNums = []
		with open(os.path.join(self._path, "Notes")) as noteFile:
			for line in noteFile:
				if line.lower().startswith('iguana'):
					colNums.append(int(line.split()[-1]))
		freqs = [int(CHANNEL_MAP[int(col)] * 1e6) for col in colNums]
		[self.tx_freq_set.add(freq) for freq in freqs]

	def loadTXT(self):
		colNums = []
		with open(glob.glob(os.path.join(os.path.dirname(self._path), "*.txt"))[0]) as noteFile:
			for line in noteFile:
				if line.lower().startswith('iguana'):
					colNums.append(int(line.split()[-1]))
		freqs = [int(CHANNEL_MAP[int(col)] * 1e6) for col in colNums]
		[self.tx_freq_set.add(freq) for freq in freqs]

	def hasDailyCSV(self):
		return self._hasDailyCSV

	def hasDailyTXT(self):
		return self._hasDailyTXT

	def setFreq(self, freqs, rejectQuiet = False):
		assert(isinstance(freqs, list))
		assert(len(freqs) > 0)
		self.tx_freq_set = set()
		for freq in freqs:
			try:
				assert(abs(freq - self.getCenterFreq()) < self.getSamplingFreq() / 2)
				self.tx_freq_set.add(freq)
			except Exception as e:
				if rejectQuiet:
					continue
				else:
					raise e

	def _hasFallingEdge(self, sequence):
		assert(isinstance(sequence, CircularBuffer))
		edges = set()
		if len(sequence) < 2:
			return edges
		for j in range(len(sequence[0])):
			if sequence[-2][j] == True and sequence[-1][j] == False:
				edges.add(j)
		return edges

	def _getTrailingRisingEdge(self, sequence, idx):
		assert(isinstance(sequence, CircularBuffer))
		if len(sequence) < 2:
			return None
		for i in range(len(sequence) - 2, -1, -1):
			if sequence[i][idx] == False and sequence[i + 1][idx] == True:
				return i+1
		return None

	def _getPulseWidth(self, sequence, idx):
		assert(isinstance(idx, int))
		assert(isinstance(sequence, CircularBuffer))
		assert(len(sequence) > 0)
		assert(idx < len(sequence[0]))
		if len(sequence) < 2:
			return None
		startIdx = self._getTrailingRisingEdge(sequence, idx)
		if startIdx is None:
			return None
		return len(sequence) - 1 - startIdx			

	def _getPulseAmplitude(self, width, dataSequence, idx):
		assert(isinstance(width, int))
		assert(width > 0)
		assert(isinstance(dataSequence, CircularBuffer))
		assert(isinstance(idx, int))
		assert(len(dataSequence) > 2)
		assert(width < len(dataSequence))
		assert(idx < len(dataSequence[0]))

		maxAmplitude = dataSequence[-1][idx]
		for i in range(-1, -1 - width, -1):
			maxAmplitude = max(dataSequence[i][idx], maxAmplitude)
		return maxAmplitude

	def process(self):

		dataFiles = sorted(self.getDataFiles())
		assert(len(dataFiles) > 0)
		assert(self.getCenterFreq() is not None)
		assert(len(self.getFreqs()) > 0)
		assert(self.getSamplingFreq() is not None)
		assert(self.getPingWidth() is not None)
		assert(self.getSamplingFreq() is not None)
		assert(self.getMinSNR() is not None)
		assert(self.getStartTime_ms() is not None)
		assert(self.getPingFactor()[0] is not None)
		assert(self.getPingFactor()[1] is not None)

		fft_bins = ((np.array(self.getFreqs()) - self.getCenterFreq()) / (self.getSamplingFreq() / 2) * FFT_LEN).astype(np.int)
		print(fft_bins)

		frequencyStepFactor = 2
		integrateTime = 6e-3
		integrateFactor = int(integrateTime * self.getSamplingFreq() / FFT_LEN * frequencyStepFactor)
		classifierInputFreq = self.getSamplingFreq() / integrateFactor  * frequencyStepFactor / FFT_LEN
		pingWidth_samp = int(self.getPingWidth() / 1000. * classifierInputFreq)
		dataLen = pingWidth_samp * 2
		maximizerLen = int(0.1 * classifierInputFreq)
		medianLen = int(1 * classifierInputFreq)
		idLen = int(0.5 * classifierInputFreq)
		readLen = int(FFT_LEN / frequencyStepFactor)
		sampleSize = 4


		integrateCounter = 0
		idIdx = 0
		sampIdx = 0
		integrator = np.zeros(len(fft_bins))
		dataBuf = CircularBuffer(dataLen)
		peakHistory = CircularBuffer(maximizerLen)
		peaks = CircularBuffer(medianLen)
		idSignal = CircularBuffer(idLen)
		dataFile = open(dataFiles[0], 'rb')
		minSNRVec = np.ones(fft_bins.shape) * self.getMinSNR()
		fftBuffer = CircularBuffer(frequencyStepFactor)
		for i in range(frequencyStepFactor):
			fftBuffer.add(np.ones(int(readLen)) * (0 + 0j))
		pings = []
		outputSignal = []
		thresholdSignal = []
		integratorSignal = []
		print("Rejecting pings narrower than %f or wider than %f" % (self.getPingFactor()[0] * self.getPingWidth(), self.getPingFactor()[1] * self.getPingWidth()))
		print("Rejecting pings with amplitude %f less than noise" % (self.getMinSNR()))
		while True:
			data = dataFile.read(readLen * sampleSize)
			if len(data) != readLen * sampleSize:
				missing = readLen * sampleSize - len(data)
				dataFiles.pop(0)
				if len(dataFiles) == 0:
					break
				dataFile = open(dataFiles[0], 'rb')
				data += dataFile.read(missing)
			block = struct.unpack("hh" * int(readLen), data)
			complexBlock = np.array([block[2*i] + block[2*i + 1] * 1j for i in range(int(readLen))]) / self.getDataScalar()
			sampIdx += FFT_LEN
			fftBuffer.add(complexBlock)
			complexFFT = np.fft.fft(fftBuffer.to_array()) / FFT_LEN
			selectFreqs = complexFFT[fft_bins]
			integrator += np.abs(selectFreqs) ** 2
			integrateCounter += 1
			if integrateCounter != integrateFactor:
				continue

			if len(dataBuf) == 0:
				for i in range(medianLen):
					peaks.add(integrator)
				for i in range(pingWidth_samp):
					peakHistory.add(integrator)
				for i in range(dataLen):
					dataBuf.add(integrator)

			dataBuf.add(integrator)
			peakHistory.add(integrator)

			peaks.add(peakHistory.max())

			threshold = np.multiply(peaks.median(), minSNRVec)
			thresholdSignal.append(threshold)
			outputSignal.append(integrator)

			# compare(sig, thresh, minSNR)
			sigCompare = integrator > threshold
			idSignal.add(sigCompare)
			idIdx += 1

			edges = self._hasFallingEdge(idSignal)
			if len(edges) > 0:
				for edge in list(edges):
					width = self._getPulseWidth(idSignal, edge)
					if width is None:
						continue
					if width > len(dataBuf) - 1:
						width = len(dataBuf) - 1
					pingStart_ms = (idIdx - width) / classifierInputFreq * 1e3
					amplitude = self._getPulseAmplitude(width, dataBuf, edge)
					if (width + 0.5) / classifierInputFreq * 1e3 < self.getPingFactor()[0] * self.getPingWidth() or (width - 0.5) / classifierInputFreq * 1e3 > self.getPingFactor()[1] * self.getPingWidth():
						print("Ping %d at %.3f ms, amplitude: %.3f, threshold: %.3f, width: %.3f ms (%d samples), freq: %d Hz, idx: %d, bin: %d rejected for length" % 
							(len(pings) + 1, pingStart_ms + self.getStartTime_ms(), amplitude, threshold[edge],
								width / classifierInputFreq * 1e3, width, self.getFreqs()[edge], edge, fft_bins[edge]))
						continue
					pings.append(Ping(pingStart_ms + self.getStartTime_ms(), amplitude, self.getFreqs()[edge], idIdx, width))
					print("Ping %d at %.3f ms, amplitude: %.3f, threshold: %.3f, width: %.3f ms (%d samples), freq: %d Hz, idx: %d, bin: %d" % 
						(len(pings), pingStart_ms + self.getStartTime_ms(), amplitude, threshold[edge],
							width / classifierInputFreq * 1e3, width, self.getFreqs()[edge], edge, fft_bins[edge]))

			integrator = np.zeros(len(fft_bins))
			integrateCounter = 0
		# end of signal processing
		return (outputSignal, thresholdSignal, pings)
		if len(pings) == 0:
			return (outputSignal, thresholdSignal)


def main():
	pass

def load2017Map():
	map_data_file = '/home/ntlhui/workspace/rct_summary_data/all_drone_data_map.csv'
	run_freq_map = {}
	with open(map_data_file) as dataFile:
		for line in dataFile:
			data = line.split(',')
			channel = int(data[0].split('_')[1])
			run = int(data[2].split('_')[1])
			if run in run_freq_map:
				run_freq_map[run].append(int(CHANNEL_MAP[int(channel)] * 1e6))
			else:
				run_freq_map[run] = [int(CHANNEL_MAP[int(channel)] * 1e6)]
	return run_freq_map

def load2019Map():
	map_data_file = '/home/ntlhui/workspace/rct_summary_data/2019.run_freq_mapping.csv'
	run_freq_map = {}
	run_good_map = {}
	with open(map_data_file) as dataFile:
		for line in dataFile:
			data = line.split(',')
			run = int(data[0])
			freq = int(data[1])
			year = int(data[2])
			month = int(data[3])
			day = int(data[4])
			goodMap = bool(data[5])
			if day not in run_freq_map:
				run_freq_map[day] = {}
				run_good_map[day] = {}
			if run not in run_freq_map[day]:
				run_freq_map[day][run] = []
				run_good_map[day][run] = True
			run_freq_map[day][run].append(freq)
			run_good_map[day][run] &= goodMap
	return run_freq_map, run_good_map

if __name__ == '__main__':
	main()
	data_path = '/media/ntlhui/FA56-CFCD/'
	run_paths = glob.glob(os.path.join(data_path, '**', 'META_*'), recursive=True)
	runs = [RCTRun(os.path.dirname(run_path)) for run_path in run_paths]
	print('Found %d runs' % (len(runs)))
	p = multiprocessing.Pool(7)
	# hasCol = [run.getPath() for run in runs if run.hasCol()]
	# [run.loadCol() for run in runs if run.hasCol()]
	# [run.setPingFactor((0.75, 2)) for run in runs if run.hasCol()]
	# [run.setMinSNR(4) for run in runs if run.hasCol()]
	# [run.setPingWidth(15) for run in runs if run.hasCol()]
	# [run.loadCol() for run in runs if run.hasCol()]
	# [run.loadColj() for run in runs if run.hasColj() and not run.hasNotes()]
	# [run.loadNotes() for run in runs if not run.hasColj() and run.hasNotes()]
	# hasNotes = [run.getPath() for run in runs if run.hasNotes()]
	# global_channel_map_2017 = load2017Map()
	# [run.setFreq(global_channel_map_2017[run.getRunNum()]) for run in runs if run.getStartTime().year == 2017 and run.getRunNum() in global_channel_map_2017]
	# [run.setPingFactor((0.75, 2)) for run in runs if run.getStartTime().year == 2017 and run.getRunNum() in global_channel_map_2017]
	# [run.setMinSNR(4) for run in runs if run.getStartTime().year == 2017 and run.getRunNum() in global_channel_map_2017]
	# [run.setPingWidth(15) for run in runs if run.getStartTime().year == 2017 and run.getRunNum() in global_channel_map_2017]
	# [run.setDataScalar(4096) for run in runs if run.getStartTime().year == 2017 and run.getRunNum() in global_channel_map_2017]
	# global_channel_map_2019, goodMap = load2019Map()
	# for run in runs:
	# 	if run.getStartTime().year == 2019 and run.getStartTime().month == 8 and run.getStartTime().day in global_channel_map_2019:
	# 		run.setFreq(global_channel_map_2019[run.getStartTime().day][run.getRunNum()], rejectQuiet = goodMap[run.getStartTime().day][run.getRunNum()])
	# 		run.setPingFactor((0.75, 1.5))
	# 		run.setPingWidth(36)
	# 		run.setDataScalar(16384)

	processable_runs = [run for run in runs if len(run.getFreqs()) > 0]
	print("Processing %s" % (processable_runs[1].getPath()))
	# retval = processable_runs[1].process()

	plt.plot(retval[0])
	plt.plot(retval[1])

	minY = min(np.min(retval[0]), np.min(retval[1]))
	maxY = max(np.max(retval[0]), np.max(retval[1]))

	for ping in retval[2]:
		ax = plt.gca()
		rect = patches.Rectangle((ping.idx - ping.width_s, minY), ping.width_s, maxY - minY, linewidth=1, edgecolor='r', facecolor='none')
		ax.add_patch(rect)

	p.map(RCTRun.writeJson, runs)

	p.close()
	print("Finished")