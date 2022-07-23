#!/usr/bin/env python3
import glob
import os
import numpy as np
import matplotlib.pyplot as plt; plt.ion()
import cv2
import utm

if __name__ == '__main__':
	runs = glob.glob('/media/ntlhui/FA56-CFCD/**/RUN_*/')

	bytes_per_sample = 4
	samples_per_second = 2000000

	run_lengths = {}
	run_map = {}
	run_gps = {}
	run_data = {}
	total_flight_time = 0
	for run in runs:
		run_num = int(os.path.basename(run.rstrip(os.path.sep)).split('_')[1])
		run_map[run_num] = run
		raw_data_files = glob.glob(os.path.join(run, "RAW_DATA_*"))
		total_data_len = 0
		for file in raw_data_files:
			total_data_len += os.path.getsize(file)
		run_length = total_data_len / bytes_per_sample / samples_per_second
		run_lengths[run_num] = run_length
		total_flight_time += run_length
		gps_file = glob.glob(os.path.join(run, "GPS_*"))
		if len(gps_file) > 0:
			if os.path.getsize(gps_file[0]) > 0:
				run_gps[run_num] = gps_file
		if len(raw_data_files) > 0:
			run_data[run_num] = raw_data_files


	summary_data_file = "/home/ntlhui/workspace/rct_summary_data/summary.csv"

	summary_dataset = {}

	run_nums = set()

	set_of_multiple_track_missions = set()
	set_of_track_with_data = set()
	summary_runs = set()
	missions_no_data = set()

	with open(summary_data_file) as summary_data:
		for line in summary_data:
			collar = int(line.split(',')[0].split('_')[1])
			date = line.split(',')[1]
			time = line.split(',')[2]
			run_num = int(line.split(',')[3].split('_')[1])
			lat = float(line.split(',')[4])
			lon = float(line.split(',')[5])
			err = float(line.split(',')[6])
			track_type = line.split(',')[7]

			summary_dataset[(run_num, collar)] = (date, time, lat, lon, err, track_type)
			if run_num in run_nums:
				set_of_multiple_track_missions.add(run_num)
			else:
				run_nums.add(run_num)

			if run_num in run_map:
				set_of_track_with_data.add(run_num)
			else:
				missions_no_data.add(run_num)

	no_track_missions = [run for run in list(run_map.keys()) if run not in run_nums]

	track_mission_times = [run_length for run_num, run_length in run_lengths.items() if run_num in set_of_track_with_data]

	bad_unicode_gps = {}

	# Calculate area
	area = 0
	area1 = 0
	radius = 80
	for run_num, gps_file in run_gps.items():
	# for gps_file in [run_gps[1]]:
		points = []
		try:
			with open(gps_file[0]) as gps_data:
				for line in gps_data:
					lat = float(line.split(',')[1]) * 1e-7
					lon = float(line.split(',')[2]) * 1e-7
					easting, northing, zone, zone_num = utm.from_latlon(lat, lon)
					if easting == 0 or northing == 0:
						continue
					points.append((int(easting), int(northing)))
			box = cv2.minAreaRect(np.array(points, dtype=np.int32))
			area += box[1][0] * box[1][1]
		except UnicodeDecodeError as e:
			bad_unicode_gps[run_num] = run_gps[run_num]
		pts = np.array(points)
		min_easting = np.min(pts[:,0])
		max_easting = np.max(pts[:,0])
		min_northing = np.min(pts[:,1])
		max_northing = np.max(pts[:,1])
		# flight_area = np.zeros((max_easting - min_easting + radius * 2, max_northing - min_northing + radius * 2), np.uint8)
		# for point in points:
			# cv2.circle(flight_area, (point[0] - min_easting + radius, point[1] - min_northing + radius), radius, (1), -1)
		# area1 += np.sum(flight_area)


	for run_num, gps_file in bad_unicode_gps.items():
		run_gps.pop(run_num)
	
	print("Total Missions: %d" % (len(runs)))
	print("Missions with tracks but no data: %d" % len(missions_no_data))
	print("Missions with tracks with data: %d" % (len(run_nums)))
	print("Missions with multiple tracks: %d" % (len(set_of_multiple_track_missions)))
	print("Missions with data: %d" % (len(runs)))
	print("Number of tracks: %d" % (len(summary_dataset)))
	print("Missions with no data: %d" % (len(runs) - len(run_data)))
	print("Missions with no GPS: %d" % (len(runs) - len(run_gps)))
	print("Missions with bad GPS data: %d" % (len(bad_unicode_gps)))
	print("Missions with no tracks: %d" % (len(runs) - len(run_nums)))
	print("Total flight time: %.2f hr" % (total_flight_time / 60 / 60))
	print("Mean Mission Time for Track: %.0f min" % (np.mean(track_mission_times) / 60))
	plt.hist(np.array(track_mission_times) / 60);
	plt.xlabel("Flight Time (min)")
	plt.ylabel("Number of Missions")
	plt.savefig("mission_time_hist.png")
	plt.close()
	print("Total area covered: %.0f km^2" % (area * 1e-6))
	print("Total area1 covered: %.0f km^2" % (area1 * 1e-6))
