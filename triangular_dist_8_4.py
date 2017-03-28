import random
import math

def run_sim(trials):
	i = 0
	total = 0.
	while (i < trials):
		i += 1
		total += 10 - (9 * math.sqrt(1 - random.uniform(0, 1)))

	return total / trials

if __name__ == '__main__':
	print str(run_sim(1000))