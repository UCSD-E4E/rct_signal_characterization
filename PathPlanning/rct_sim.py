#!/usr/bin/env python
import utm
import numpy as np
import shapefile as shp
from scipy.optimize import leastsq

def model(pos, params, sigma = 0):
	tx_location = np.array([params[2], params[3], 0])
	k1 = params[0]
	k2 = params[1]

	distance = np.linalg.norm(tx_location - pos)

	rx_pow = k1 - 10 * k2 * np.log10(distance) + np.random.normal(0, sigma)

	return rx_pow


def residuals(params, data):
	rx_pow = data[:,0]
	pos = data[:,1:4]
	residual = np.zeros(len(rx_pow))
	for i in xrange(len(rx_pow)):
		residual[i] = model(pos[i,:], params) - rx_pow[i]
	return residual


if __name__ == '__main__':
	waypoints_file = open('fast_plan.waypoints')
	waypoints_file.readline()

	waypoints = []
	homeline = waypoints_file.readline().strip()
	home_lat = float(homeline.split()[8])
	home_lon = float(homeline.split()[9])

	takeoff_line = waypoints_file.readline().strip()
	# takeoff_line = homeline
	takeoff_lat = float(takeoff_line.split()[8])
	takeoff_lon = float(takeoff_line.split()[9])
	(easting, northing, zone_num, zone_letter) = utm.from_latlon(takeoff_lat, takeoff_lon)
	waypoints.append([easting, northing, 30.0])

	do_change_speed_line = waypoints_file.readline().strip()
	speed = float(do_change_speed_line.split()[5])

	waypoint_line = waypoints_file.readline().strip()
	while waypoint_line.split()[3] == "16":
		waypoint_lat = float(waypoint_line.split()[8])
		waypoint_lon = float(waypoint_line.split()[9])
		waypoint_alt = float(waypoint_line.split()[10])
		(easting, northing, zone_num, zone_letter) = utm.from_latlon(waypoint_lat, waypoint_lon)
		waypoints.append([easting, northing, waypoint_alt])
		waypoint_line = waypoints_file.readline().strip()

	(easting, northing, zone_num, zone_letter) = utm.from_latlon(home_lat, home_lon)
	waypoints.append([easting, northing, 30.0])


	measurement_location = np.array(waypoints[0])
	data = np.zeros((0, 4))

	tx_lat = 19.665405
	tx_lon = -80.102354
	(easting, northing, zone_num, zone_letter) = utm.from_latlon(tx_lat, tx_lon)

	noise_floor = 40

	params = (80, 2, easting, northing, 0)
	estimate = (79, 1, waypoints[0][0], waypoints[0][1], 0)
	history = []
	s_per_ping = 1.0
	for i in xrange(len(waypoints) - 1):
		start_waypoint = np.array(waypoints[i])
		end_waypoint = np.array(waypoints[i+1])
		distance = np.linalg.norm(end_waypoint - start_waypoint)
		num_measurements = distance / speed / s_per_ping

		itr_vec = (end_waypoint - start_waypoint) / distance * speed * s_per_ping
		
		for k in xrange(int(np.floor(num_measurements))):
			result = model(measurement_location, params, 0.5)
			if result > noise_floor:
				data = np.append(data, np.array([result, measurement_location[0], measurement_location[1], measurement_location[2]]).reshape((1,4)), 0)
				if len(data) > 5:
					x, cov_x, infodict, mesg, ier = leastsq(residuals, estimate, args=(data), full_output = 1)
					# errors = res
					errors = residuals(x, data)
					history.append((x, np.mean(errors), np.std(errors)))
					estimate = x
			measurement_location += itr_vec

	w = shp.Writer(shp.POLYLINE)
	w.field('name', "C")
	line = [[]]
	for waypoint in waypoints:
		(lat, lon) = utm.to_latlon(waypoint[0], waypoint[1], zone_num, zone_letter)
		line[0].append([lon, lat])
	w.line(line)
	w.record("Flight Path")
	w.save('flightpath.shp')

	w = shp.Writer(shp.POINT)
	w.autoBalance = 1
	w.field('lon', 'F', 20, 18)
	w.field('lat', 'F', 20, 18)
	w.field('alt', 'F', 18, 18)
	w.field('tx_pow', "F", 18, 18)
	w.field('order', 'F', 18, 18)
	w.field('error_mean', 'F', 18, 18)
	w.field('error_std', 'F', 18, 18)
	w.field('sequence', 'N', 18, 0)
	# for result in history:
	for i in xrange(len(history)):
		result = history[i]
		estimate = result[0]
		mean_error = result[1]
		std_error = result[2]
		(lat, lon) = utm.to_latlon(estimate[2], estimate[3], zone_num, zone_letter)
		w.point(lon, lat)
		w.record(lon, lat, estimate[4], estimate[0], estimate[1], mean_error, std_error, i)
	w.save("estimate.shp")
	
	w = shp.Writer(shp.POINT)
	w.autoBalance = 1
	w.field("lon", "F", 20, 18)
	w.field("lat", "F", 20, 18)
	w.field("alt", "F", 18, 18)
	w.field("measurement", "F", 18, 18)

	for datapoint in data:
		(lat, lon) = utm.to_latlon(datapoint[1], datapoint[2], zone_num, zone_letter)
		# print("(%f, %f)" % (lat, lon))
		w.point(lon, lat)
		w.record(lon, lat, datapoint[3], datapoint[0])
	w.save('output.shp')

	prj = open('output.prj', "w")
	epsg = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
	prj.write(epsg)
	prj.close()

	prj = open('estimate.prj', "w")
	epsg = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
	prj.write(epsg)
	prj.close()

	prj = open('flightpath.prj', "w")
	epsg = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
	prj.write(epsg)
	prj.close()
