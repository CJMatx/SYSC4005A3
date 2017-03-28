import numpy as np
import math
from scipy.stats import chi2
import matplotlib.pyplot as plt

INTERARRIVAL_MEAN = 1
SERVICE_MEAN = 0.6
MAX_DEPARTURES = 1000
CHI_SQUARE_VALUES = [3.84, 5.99, 7.81, 9.49, 11.07, 12.59, 14.07, 15.51, 16.92, 18.31,
						19.68, 21.03, 22.36, 23.68, 25., 26.3, 27.59, 28.87, 30.14, 31.41]

occupancy = []
event_list = []
interarrival_times = []
service_times = []
arrival_times = []
departure_times = []
time = 0
queue_length = 0
server_length = 0
departures = 0

def run_sim():
	global interarrival_times, service_times, event_list, time
	# generate exponential times
	interarrival_times = np.random.exponential(INTERARRIVAL_MEAN, MAX_DEPARTURES)
	service_times = np.random.exponential(SERVICE_MEAN, MAX_DEPARTURES)

	event_list = [("arrival", interarrival_times[0])] # set first arrival event
	interarrival_times = np.delete(interarrival_times, 0)

	while (event_list):
		# print departures
		event = event_list.pop(0)
		time = event[1]
		if (event[0] == "arrival"):
			arrival()
		else:
			depart()

def arrival():
	global server_length, queue_length, service_times, interarrival_times, occupancy, arrival_times
	occupancy.append(server_length + queue_length)
	arrival_times.append(time)
	if (server_length == 0):
		server_length = 1
		insert_event(("departure", time + service_times[0]))
		service_times = np.delete(service_times, 0)
	else:
		queue_length += 1

	if (interarrival_times.size == 0):
		return

	insert_event(("arrival", time + interarrival_times[0]))
	interarrival_times = np.delete(interarrival_times, 0)

def depart():
	global departures, queue_length, server_length, service_times, departure_times
	departure_times.append(time)
	departures += 1
	if (departures == MAX_DEPARTURES):
		return

	if (queue_length > 0):
		queue_length -= 1
		insert_event(("departure", time + service_times[0]))
		service_times = np.delete(service_times, 0)
	else:
		server_length = 0

def insert_event(event):
	global event_list
	for i in range(0, len(event_list)):
		if (event[1] < event_list[i][1]):
			event_list.insert(i, event)
			return

	event_list.append(event)

def chi_square(observed, expected):
	i = len(observed) - 1
	while (i > 0):
		if (expected[i] < 5):
			observed[i-1] = observed[i-1] + observed.pop(i)
			expected[i-1] = expected[i-1] + expected.pop(i)
		i-=1

	# result = scipy.stats.chisquare(observed, f_exp=expected, ddof=1)
	dof = len(observed) - 2
	result = 0
	for i in range(len(observed)):
		result += ((observed[i] - expected[i])**2) / expected[i]

	print "Degrees of freedom: " + str(dof)
	print "Chi-Square: " + str(result)
	print "Test Value: " + str(chi2.isf(0.05, dof))
	if (result < chi2.isf(0.05, dof)):
		print "TEST PASSED"
	else:
		print "TEST FAILED"

def expected_value(upper_limit, lower_limit, rate):
	upper_prob = 1 - math.exp(-1.0 * rate * upper_limit)
	lower_prob = 1 - math.exp(-1.0 * rate * lower_limit)
	return MAX_DEPARTURES * (upper_prob - lower_prob)

run_sim()

occupancy_frequency = []
num_bins = 0
for i in range(0, max(occupancy) + 1):
	occupancy_frequency.append(0)
	num_bins += 1

for i in occupancy:
	occupancy_frequency[i] += 1

server_utilization = (departures - occupancy_frequency[0]) / float(departures)
# server_utilization_2 = departures / float(sum(occupancy) + departures)
# print server_utilization_2

expected_frequency = []
for i in range(0, len(occupancy_frequency) + 1):
	expected_frequency.append(departures * (server_utilization**i) * (1 - server_utilization))

print "Server Utilization: " + str(server_utilization)

chi_square(occupancy_frequency, expected_frequency)

# plt.hist(occupancy, num_bins)
# plt.xlabel("PACKET OCCUPANCY OF SYSTEM ON NEW ARRIVAL")
# plt.ylabel("FREQUENCY OF OCCUPANCY")
# plt.title("System Occupancy")
# plt.show()

waiting_time = []
for i in range(len(arrival_times)):
	waiting_time.append(departure_times[i] - arrival_times[i])

freq, bins = np.histogram(waiting_time, 32)
for i in range(len(freq)):
	print "BIN: " + str(bins[i]) + " FREQ: " + str(freq[i])

waiting_time_rate = float(len(waiting_time)) / float(sum(waiting_time))

bin_diff = bins[1] - bins[0]

expected = []
for i in range(len(freq)):
	expected.append(expected_value(bins[i] + bin_diff, bins[i], waiting_time_rate))
	
print expected
print sum(expected)
print len(freq)

chi_square(freq.tolist(), expected)

plt.hist(waiting_time, 32)
plt.xlabel("WAITING TIME OF PACKET")
plt.ylabel("FREQUENCY OF WAITING TIME")
plt.title("Waiting Time")
plt.show()