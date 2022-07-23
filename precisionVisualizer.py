#!/usr/bin/env python3
import numpy as np
import os
import threading
import utm
import json
from scipy.optimize import least_squares
import scipy.stats
import matplotlib.pyplot as plt; plt.ion()

class Ping:
	'''
	Ping class.  Contains the ping's time of acquire in ms since Unix Epoch,
	latitude and longitude in decimal degrees WGS84, altitude/z in m above the
	WGS84 spheroid, relative amplitude, and location in UTM coordinates.
	'''
	def __init__(self, time, lat, lon, alt, amp):
		'''
		Creates a new Ping object

		Parameters:
		time	Time in ms since Unix Epoch
		lat		Latitude in decimal degrees
		lon		Longitude in decimal degrees
		alt		Altitude in m above sea level
		amp		Amplitude (relative) of ping in dB
		'''
		self.time = time
		self.lat = lat
		self.lon = lon
		self.z = alt
		self.amp = amp
		(self.x, self.y, self.zonenum, self.zone) = utm.from_latlon(self.lat, self.lon)

	def range(self, params):
		distance = 10 ** (((params[0] * self.amp + params[1]) / 10.0))
		stdev = 0.4 * distance
		return (distance, stdev)

	def pos(self):
		return np.array([self.x, self.y])

class PingFactory:
	def fromJSON(self, string):
		pingDict = json.loads(string)
		if 'ping' not in pingDict:
			return None
		try:
			return Ping(pingDict['ping']['time'],
						pingDict['ping']['lat'] / 1e7,
						pingDict['ping']['lon'] / 1e7,
						pingDict['ping']['alt'],
						pingDict['ping']['amp'])
		except:
			return None

def residuals(param, amp, pos):
	residual = np.zeros(len(amp))
	est = np.array([param[2], param[3], 0])
	for i in range(len(amp)):
		residual[i] = 10 ** (((param[0] * amp[i] + param[1]) / 10.0)) - np.linalg.norm(pos[i] - est)
	return residual

class PrecisionVisualizer:
	"""docstring for PrecisionVisualizer"""
	def __init__(self, path, live = True, resolution = 1):
		self.path = path
		assert(os.path.isfile(path))
		self.live = live
		self.resolution = resolution # in m / pixel
		if self.live:
			self._thread = threading.Thread(target=self.process)
			self._thread.start()
		else:
			self._thread = None
		self.iToW = np.eye(3)
		self.image = None
		self.extents_w = None
		self.size = np.zeros(2) # in pixels
		self.pings = []
		self.est_params = np.array([-0.715, -14.51, 0, 0])

	def stop(self):
		self.live = False

	def process(self):
		pFact = PingFactory()
		with open(self.path) as localizeFile:
			# read all data in
			for line in localizeFile:
				pingCandidate = pFact.fromJSON(line)
				if pingCandidate is not None:
					self.pings.append(pingCandidate)
			# calculate extents, if present
			pingData = np.array([(ping.x, ping.y, ping.z, ping.amp) for ping in self.pings])
			if len(self.pings) > len(self.est_params):
				maxExtents = np.amax(pingData, axis=0)
				minExtents = np.amin(pingData, axis=0)
				avgExtents = np.mean(pingData, axis=0)
				self.est_params[2] = avgExtents[0]
				self.est_params[3] = avgExtents[1]

				# calculate estimate, if availble
				est_res = least_squares(residuals, self.est_params, bounds=((-np.inf, -np.inf, 100000, 1000000), (np.inf, np.inf, 900000, 9800000)), args=(pingData[:,3], pingData[:,0:3]))
				if est_res.status:
					self.est_params = est_res.x
					print(self.est_params)
					extremaExtents = np.block([[maxExtents], [minExtents], [avgExtents], [np.array([self.est_params[2], self.est_params[3], 0, 0])]])
					print(extremaExtents)
					maxExtents = np.amax(pingData, axis=0)
					minExtents = np.amin(pingData, axis=0)

					# plot
					self.size = np.ceil((maxExtents[0:2] - minExtents[0:2]) / self.resolution).astype(np.int) # (x, y)
					actualResolution = np.divide((maxExtents[0:2] - minExtents[0:2]), self.size) # m / pixel (x, y)
					self.image = np.zeros(self.size + np.array([1, 1])).transpose()
					self.iToW = np.array([[0, -1 / actualResolution[1], maxExtents[1] / actualResolution[1]], 
										  [1 / actualResolution[0], 0, -minExtents[0] / actualResolution[0]], 
										  [0, 0, 1]])
					for ping in self.pings:
						self.addPing(ping)
						return
			while self.live:
				# keep going
				line = localizeFile.readline()
				if line == '':
					continue
				pingDict = json.loads(line)
				if 'ping' in pingDict:
					self.pings.append(Ping(pingDict['ping']['time'],
										   pingDict['ping']['lat'] / 1e7,
										   pingDict['ping']['lon'] / 1e7,
										   pingDict['ping']['alt'],
										   pingDict['ping']['amp']))
				if self.image is None:
					maxExtents = np.amax(pingData, axis=0)
					minExtents = np.amin(pingData, axis=0)
					avgExtents = np.mean(pingData, axis=0)
					self.est_params[2] = avgExtents[0]
					self.est_params[3] = avgExtents[1]

					# calculate estimate, if availble
					est_res = least_squares(residuals, self.est_params, bounds=((-np.inf, -np.inf, 100000, 1000000), (np.inf, np.inf, 900000, 9800000)), args=(pingData[:,3], pingData[:,0:3]))
					if not est_res.status:
						continue
					self.est_params = est_res.x
					print(self.est_params)
					extremaExtents = np.block([[maxExtents], [minExtents], [avgExtents], [np.array([self.est_params[2], self.est_params[3], 0, 0])]])
					print(extremaExtents)
					maxExtents = np.amax(pingData, axis=0)
					minExtents = np.amin(pingData, axis=0)

					# plot
					self.size = np.ceil((maxExtents[0:2] - minExtents[0:2]) / self.resolution).astype(np.int) # (x, y)
					actualResolution = np.divide((maxExtents[0:2] - minExtents[0:2]), self.size) # m / pixel (x, y)
					self.image = np.zeros(self.size + np.array([1, 1])).transpose()
					self.iToW = np.array([[0, -1 / actualResolution[1], maxExtents[1] / actualResolution[1]], 
										  [1 / actualResolution[0], 0, -minExtents[0] / actualResolution[0]], 
										  [0, 0, 1]])
				self.addPing(ping)


	def addPing(self, ping):
		if self.image is None:
			return
		errorParams = ping.range(self.est_params[0:2])
		for u in range(self.size[1]): # row
			for v in range(self.size[0]): # column
				pixel = np.matmul(np.linalg.inv(self.iToW), np.array([[u, v, 1]]).transpose())
				# print(pixel)
				dist = np.linalg.norm(pixel[0:2] - self.est_params[2:4])
				prob = scipy.stats.norm.pdf(dist, errorParams[0], errorParams[1])
				# print(dist, prob)
				if prob > 1e-3:
					self.image[u,v] += np.log10(scipy.stats.norm.pdf(dist, errorParams[0], errorParams[1]))

	def getImage(self):
		return self.image


if __name__ == '__main__':
	testFile = '/media/ntlhui/FA56-CFCD/2019.08.09.Successful_Night_Tracking/RUN_000069/LOCALIZE_000069'
	visualizer = PrecisionVisualizer(testFile, live = False)
	visualizer.process()
	# visualizer.stop()
	plt.imshow(np.power(10, visualizer.getImage()))

	fig = plt.figure()
	plt.scatter(visualizer.est_params[2], visualizer.est_params[3], marker='+', color='blue')
	for ping in visualizer.pings:
		plt.scatter(ping.x, ping.y, marker='^', color='red')
		cir = plt.Circle((ping.x, ping.y), radius=ping.range(visualizer.est_params)[0], fill=False, edgecolor='red')
		fig.gca().add_artist(cir)

