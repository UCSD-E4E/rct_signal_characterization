#!/usr/bin/env python3

import matplotlib.pyplot as plt; plt.ion()

if __name__ == '__main__':
	times = [5, 5, 0.5, 0.25, 0.5]
	labels = [
			  'Flight Time',
			  'Post-Processing',
			  'Mission Planning',
			  'Data Transfer',
			  'Data Visualization']
	plt.pie(times, labels = labels, autopct='%.f%%', startangle=180+0.06*360)
	plt.title('Mission Time Distribution')
	plt.savefig('mission_time_dist.png')
	plt.close()