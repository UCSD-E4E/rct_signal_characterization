#!/usr/bin/env python2

import os
import argparse
import glob
import get_beat_frequency
import subprocess
import median_filter
import pos_estimator
import csvToShp
import raw_gps_analysis

class RCTRun(object):
	"""docstring for RCTRun"""
	def __init__(self, data_dir, run_num):
		self.data_dir = data_dir
		self.run_num = run_num
		self.has_gps = False
		self.has_meta = False
		self.has_colj = False
		self.has_col = False
		self.num_data_files = 0
		self.has_alt = False
		self.sdr_start_time = 0
		self.sdr_end_time = 0
		self.gps_start_time = 0
		self.gps_end_time = 0
		self.freq = []
	def __str__(self):
		return "{RCT Run %06d: %s, Data files: %d, Complete: %r, length: %d, "\
			"gps_start: %d, gps_end: %d, sdr_start: %d, sdr_end: %d, freqs: %r}" % \
			(self.run_num, self.data_dir, self.num_data_files, 
				self.hasCompleteAttr(), self.gps_end_time - self.gps_start_time,
				self.gps_start_time, self.gps_end_time, self.sdr_start_time,
				self.sdr_end_time, self.freq)
	def __repr__(self):
		return self.__str__()
	def setHasGPS(self, has_gps):
		self.has_gps = has_gps
	def setHasMETA(self, has_meta):
		self.has_meta = has_meta
	def setHasCOLJ(self, has_colj):
		self.has_colj = has_colj
	def setHasCOL(self, has_col):
		self.has_col = has_col
	def setNumData(self, num_files):
		self.num_data_files = num_files
	def setHasAlt(self, has_alt):
		self.has_alt = has_alt
	def hasCompleteAttr(self):
		if self.has_gps and self.has_meta and self.has_col:
			return True
		else:
			return False
	def initData(self):
		if not self.hasCompleteAttr():
			return False
		meta_file = glob.glob(os.path.join(self.data_dir, "META_*"))[0]
		with open(meta_file) as meta_data:
			for line in meta_data:
				if line.strip().split(": ")[0] == "start_time":
					self.sdr_start_time = (float)(line.strip().split(": ")[1])
				if line.strip().split(": ")[0] == "center_freq":
					self.center_freq = (int)(line.strip().split(": ")[1])
				if line.strip().split(": ")[0] == "sampling_freq":
					self.sampling_freq = (int)(line.strip().split(": ")[1])
				if line.strip().split(": ")[0] == "gain":
					self.gain = (float)(line.strip().split(": ")[1])

		# Check GPS
		with open(glob.glob(os.path.join(self.data_dir, "GPS_*"))[0]) as gps_data:
			self.gps_start_time = 2147483647.0;
			self.gps_end_time = 0;
			for line in gps_data:
				time = (float)(line.strip().split(", ")[0])
				if time < self.gps_start_time:
					self.gps_start_time = time
				if time > self.gps_end_time:
					self.gps_end_time = time

		# Check data
		data_bytes = 0
		for i in range(self.num_data_files):
			data_bytes += os.path.getsize(os.path.join(self.data_dir, "RAW_DATA_%06d_%06d" % (self.run_num, i+1)))
		self.sdr_end_time = self.sdr_start_time + data_bytes / 4 / self.sampling_freq
		if self.gps_end_time + 5 < self.sdr_end_time:
			return False

		# Get frequencies
		with open(os.path.join(self.data_dir, "COL")) as col:
			self.freq = []
			for line in col:
				self.freq.append((int)(line.strip().split(": ")[1]))
		return True
		
def printBadRuns(filename, dict):
	with open(filename, 'w') as run_file:
		for num, run in dict.items():
			run_file.write("Run %06d,\t%s\n\t%r\n" % (run.run_num, run.data_dir, run))

def processRun(run):
	beat_frequencies = [get_beat_frequency.getBeatFreq(run.center_freq, freq, 0) for freq in run.freq]
	# print(beat_frequencies)
	args = ""
	args += " -i %s " % (run.data_dir)
	args += " -o %s " % (run.data_dir)
	args += " -r %d " % (run.run_num)
	args += " -- "
	for freq in beat_frequencies:
		args += " %s " % (freq)
	subprocess.call(os.path.join(os.sep, "usr", "local", "bin", "fft_detect") + args, shell=True)
	for i in range(len(run.freq)):
		raw_gps_analysis.process(run.data_dir, run.data_dir, run.run_num, i + 1, 30)
		data_file = '%s/RUN_%06d_COL_%06d.csv' % (run.data_dir, run.run_num, i + 1)
		csvToShp.create_shapefile(data_file, '%s/RUN_%06d_COL_%06d.shp' % (run.data_dir, run.run_num, i + 1))
		start_location = median_filter.generateGraph(run.run_num, i + 1, data_file, run.data_dir, os.path.join(run.data_dir, "COL"))
		res_x = pos_estimator.generateGraph(run, i + 1, data_file, data_dir, os.path.join(run.data_dir, "COL"), start_location)
		print res_x



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Batch Processor")
	parser.add_argument('--data', '-d', type=str, help='Data Directory', default='/home/ntlhui/workspace/rct_data/')
	args = parser.parse_args()
	
	data_dir = args.data

	run_dirs = glob.glob(os.path.join(data_dir, 'RUN_*'))
	runs = {}
	for run_dir in run_dirs:
		GPS_data_file = glob.glob(os.path.join(run_dir, "GPS_*"))
		META_file = glob.glob(os.path.join(run_dir, "META_*"))
		DATA_files = glob.glob(os.path.join(run_dir, "RAW_DATA_*"))
		COLJ_file = glob.glob(os.path.join(run_dir, "COLJ"))
		COL_file = glob.glob(os.path.join(run_dir, "COL"))
		ALT_file = glob.glob(os.path.join(run_dir, "ALT"))
		if not META_file:
			continue
		run_num = (int)(os.path.basename(run_dir).split("_")[1])
		runs[run_num] = RCTRun(run_dir, run_num)
		runs[run_num].setHasGPS(len(GPS_data_file) == 1)
		runs[run_num].setHasMETA(len(META_file) == 1)
		runs[run_num].setHasCOLJ(len(COLJ_file) == 1)
		runs[run_num].setHasCOL(len(COL_file) == 1)
		runs[run_num].setHasAlt(len(ALT_file) == 1)
		runs[run_num].setNumData(len(DATA_files))

	inc_runs = dict([(k, r) for k, r in runs.items() if not r.hasCompleteAttr()])
	printBadRuns('incomplete_runs.csv', inc_runs)

	runs_with_col = dict([(k, r) for k, r in runs.items() if r.hasCompleteAttr()])
	runs_with_complete_data = dict([(k, r) for k, r in runs_with_col.items() if r.initData()])

	badGPSruns = dict([(k, r) for k, r in runs_with_col.items() if r.gps_end_time < r.sdr_end_time])
	printBadRuns('bad_gps_runs.csv', badGPSruns)
	print(badGPSruns)

	# Process
	for k, run in runs_with_complete_data.items():
		processRun(run)
