#!/usr/bin/env python3

import os
import shutil
import glob
import numpy as np
import matplotlib.pyplot as plt; plt.ion()

from enum import Enum

class RunStatus(Enum):
	NONE = 0
	BAD_SDR = 1
	TRACK = 2
	NOT_DETECTED = 3
	BAD_GPS = 4
	POWER_FAILURE = 5

class Track:
	def __init__(self, run, collar = -1, status = RunStatus.NONE):
		self.run = run
		self.collar = collar
		self.status = status
	def setLoc(self, lat, lon):
		self.lat = lat
		self.lon = lon
	def setErr(self, err):
		self.err = err
	def setTime(self, time):
		self.time = time
	def setStatus(self, status):
		self.status = status
	def setDate(self, date):
		self.date = date

if __name__ == '__main__':
	notes = glob.glob("/home/ntlhui/googledrive/data/2017.08.Caymans/2017**/RUN_**/Notes")
	tracks = []
	for note in notes:
		run_dir = os.path.basename(os.path.dirname(note))
		run_num = (int)(run_dir.split("_")[1])
		date = os.path.basename(os.path.dirname(os.path.dirname(note)))
		# print(note)
		with open(note) as data:
			line = data.readline().strip()
			if line == "Bad SDR data":
				tracks.append(Track(run_num, status=RunStatus.BAD_SDR))
				tracks[-1].setDate(date)
			elif line.startswith("Iguana"):
				collar = (int)(line.split(" ")[1])
				tracks.append(Track(run_num, collar, RunStatus.TRACK))
				tracks[-1].setDate(date)
				
				line = data.readline().strip()
				if line == "Iguana not detected!":
					tracks[-1].setStatus(RunStatus.NOT_DETECTED)
				else:
					lat = (float)(line.split(", ")[0])
					lon = (float)(line.split(", ")[1])
					tracks[-1].setLoc(lat, lon)

					line = data.readline().strip()
					err = (float)(line.split(" ")[1])
					tracks[-1].setErr(err)

				line = data.readline().strip()
				time = line
				tracks[-1].setTime(time)
			elif line == "Bad GPS":
				tracks.append(Track(run_num, status=RunStatus.BAD_GPS))
				tracks[-1].setDate(date)
			elif line == "Power failure":
				tracks.append(Track(run_num, status=RunStatus.POWER_FAILURE))
				tracks[-1].setDate(date)
			else:
				print(line)
	failed_tracks = [track for track in tracks if track.status == RunStatus.NOT_DETECTED]
	sdr_failed = [track for track in tracks if track.status == RunStatus.BAD_SDR]
	bad_gps = [track for track in tracks if track.status == RunStatus.BAD_GPS]
	bad_power = [track for track in tracks if track.status == RunStatus.POWER_FAILURE]

	good_tracks = [track for track in tracks if track.status == RunStatus.TRACK]
	errors = np.array([track.err for track in good_tracks])
	transmitters = {track.collar for track in tracks}
	dates = {track.date for track in tracks}
	transmitters_per_day = {}
	tracks_per_day = {}
	for date in dates:
		transmitters_per_day[date] = 0
		tracks_per_day[date] = 0
	for track in good_tracks:
		tracks_per_day[track.date] += 1

	print("Median Error: %d" % (np.median(errors)))
	print("Max operational pace: %d" % (np.max(np.array(list(tracks_per_day.values())))))
	print("Mean operational pace: %.1f" % (np.mean(np.array(list(tracks_per_day.values())))))
	print("Total Missions: %d" % (len(tracks)))
	print("Successful tracks: %d" % (len(good_tracks)))
	print("Successful mission with no track: %d" % (len(failed_tracks)))
	print("Radio Failure: %d" % (len(sdr_failed)))
	print("GPS Failure: %d" % (len(bad_gps)))
	print("Power Failure: %d" % (len(bad_power)))

	fig = plt.figure()
	plt.hist(np.log10(errors), density=True)
	plt.xlabel("log(error)")
	plt.ylabel('Count of runs')
	plt.savefig("log_error_histogram.png")
	plt.close()

	fig = plt.figure()
	plt.bar(range(len(tracks_per_day)), [tracks_per_day[date] for date in sorted(tracks_per_day)], align='center')
	plt.xticks(range(len(tracks_per_day)), sorted(tracks_per_day.keys()), rotation='vertical')
	plt.tight_layout()
	plt.ylabel("Number of Tracks")
	plt.savefig("operations_pace.png")
	plt.close()

