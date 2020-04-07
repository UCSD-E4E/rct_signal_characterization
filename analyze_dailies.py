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
	TRIANGULATED = 6

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
	summary_report = "/home/ntlhui/workspace/rct_summary_data/summary.csv"
	tracks = []
	with open(summary_report) as report:
		for line in report:
			data = line.strip().split(",")
			collar = (int)(data[0].split("_")[1])
			date = data[1]
			time = data[2]
			run_num = (int)(data[3].split("_")[1])
			lat = (float)(data[4])
			lon = (float)(data[5])
			error = (int)(data[6])
			tracks.append(Track(run_num, collar, status=RunStatus.TRACK))
			tracks[-1].setLoc(lat, lon)
			tracks[-1].setErr(error)
			tracks[-1].setTime(time)
			tracks[-1].setDate(date)

	triangulation_report = '/home/ntlhui/workspace/rct_summary_data/triangulation_summary.csv'
	ttracks = []
	with open(triangulation_report) as report:
		for line in report:
			data = line.strip().split(',')
			collar = (int)(data[0].split("_")[1])
			date = data[1]
			time = data[2]
			log_num = (int)(data[3])
			lat = (float)(data[4])
			lon = (float)(data[5])
			error = (int)(data[6])
			ttracks.append(Track(log_num, collar, status=RunStatus.TRIANGULATED))
			ttracks[-1].setLoc(lat, lon)
			ttracks[-1].setErr(error)
			ttracks[-1].setTime(time)
			ttracks[-1].setDate(date)

	# failed_tracks = [track for track in tracks if track.status == RunStatus.NOT_DETECTED]
	# sdr_failed = [track for track in tracks if track.status == RunStatus.BAD_SDR]
	# bad_gps = [track for track in tracks if track.status == RunStatus.BAD_GPS]
	# bad_power = [track for track in tracks if track.status == RunStatus.POWER_FAILURE]

	good_tracks = [track for track in tracks if track.status == RunStatus.TRACK]
	errors = np.array([track.err for track in good_tracks if track.err > 0])
	transmitters = {track.collar for track in tracks}
	dates = {track.date for track in tracks}
	tracks_per_day = {}
	for date in dates:
		tracks_per_day[date] = 0
	for track in good_tracks:
		tracks_per_day[track.date] += 1
	run_nums = [track.run for track in tracks]

	terrors = np.array([track.err for track in ttracks if track.err > 5])

	print("Days of operations: %d" % (len(dates)))
	print("Transmitters: %d" % (len(transmitters)))
	print("Median Error: %d" % (np.median(errors)))
	print("Max operational pace: %d" % (np.max(np.array((list)(tracks_per_day.values())))))
	print("Mean operational pace: %.1f" % (np.mean(np.array((list)(tracks_per_day.values())))))
	print("Total Missions: %d" % (np.max(np.array(run_nums))))
	print("Successful tracks: %d" % (len(good_tracks)))
	# print("Successful mission with no track: %d" % (len(failed_tracks)))
	# print("Radio Failure: %d" % (len(sdr_failed)))
	# print("GPS Failure: %d" % (len(bad_gps)))
	# print("Power Failure: %d" % (len(bad_power)))

	fig = plt.figure()
	n, bins = np.histogram(np.log10(np.block([errors, terrors])))
	error_hist_n, error_bins = np.histogram(errors, bins=np.power(10, bins))
	error_hist_n = error_hist_n / len(errors)
	terror_hist_n, terror_bins = np.histogram(terrors, bins=np.power(10, bins))
	terror_hist_n = terror_hist_n / len(terrors)

	widths = widths = np.array([error_bins[i+1] - error_bins[i] for i in range(len(error_bins) - 1)])

	plt.bar(error_bins[0:-1], error_hist_n, width=widths)
	plt.bar(error_bins[0:-1], terror_hist_n, width=widths)

	fig.gca().set_xscale('log')
	plt.xticks([10, 20, 40, 60, 100, 200], ['10', '20', '40', '60', '100', '200'])
	plt.yticks([0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3], ['0', '5%', '10%', '15%', '20%', '25%', '30%'])
	plt.xlabel("Certainty Radius (m)")
	plt.ylabel('Percentatge of tracks')
	plt.legend()
	plt.savefig("log_error_histogram.png")
	plt.close()

	fig = plt.figure()
	plt.bar(range(len(tracks_per_day)), [tracks_per_day[date] for date in sorted(tracks_per_day)], align='center')
	plt.xticks(range(len(tracks_per_day)), sorted(tracks_per_day.keys()), rotation='vertical')
	plt.ylabel("Number of Tracks")
	plt.tight_layout()
	plt.savefig("operations_pace.png")
	plt.close()

