#!/usr/bin/env python3

import matplotlib.pyplot as plt; plt.ion()
import numpy as np
from scipy import stats as st

width = 100

dist = 50



if __name__ == '__main__':
	field = np.zeros((2 * width, 2 * width))
	origin = np.array([width, width])
	stddev = 0.4 * dist
	mean = dist
	rv = st.norm(loc = dist, scale = stddev)
	for x in range(field.shape[0]):
		for y in range(field.shape[1]):
			r = np.linalg.norm(np.array([x, y]) - origin)
			field[x, y] = rv.pdf(r)
	fig = plt.figure()
	plt.imshow(field, extent=(-width, width, -width, width), origin='lower')
	plt.scatter(0, 0, marker='^', color='red')
	cir = plt.Circle((0, 0), radius=dist, fill=False, edgecolor='red')
	fig.gca().add_artist(cir)
	plt.xlabel('Easting (m)')
	plt.ylabel('Northing (m)')
	plt.title('Certainty Distribution for a Single Ping')
	plt.savefig('single_dist.png')
	# plt.close()


	width = 120
	pings = [np.array([-dist, 0]), np.array([0, -dist]), np.array([.7*dist, .7*dist])]
	field = np.zeros((2 * width, 2 * width))
	origin = np.array([width, width])
	stddev = 0.4 * dist
	mean = dist
	rv = st.norm(loc = dist, scale = stddev)
	for x in range(field.shape[0]):
		for y in range(field.shape[1]):
			for ping in pings:
				r = np.linalg.norm(np.array([x, y]) - origin - ping)
				field[x, y] += np.log10(rv.pdf(r))
	fig1 = plt.figure()
	plt.imshow(np.power(10, field), extent=(-width, width, -width, width), origin='lower')
	for ping in pings:
		plt.scatter(ping[0], ping[1], marker='^', color='red')
		cir = plt.Circle(ping, radius=dist, fill=False, edgecolor='red')
		fig1.gca().add_artist(cir)
	plt.xlabel('Easting (m)')
	plt.ylabel('Northing (m)')
	plt.title('Certainty Distribution for a Three Pings')
	plt.savefig('mult_dist.png')
	# plt.close()
