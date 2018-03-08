import pandas as pd
import numpy as np

data = pd.read_csv('Research+Study_March+8%2C+2018_15.56.csv')


def likert_int(s):
	if s == 'Definitely false':
		return 1
	elif s == 'Probably false':
		return 2
	elif s == 'Neutral':
		return 3
	elif s == 'Probably true':
		return 4
	elif s == 'Definitely true':
		return 5
	return 0


def combine_ans(a, b):
	res = []
	for x, y in zip(a, b):
		if x == 0:
			res.append(y)
		elif y == 0:
			res.append(x)
		else:
			print "both non-zero"
			res.append(0)
	return res

def process_claim(data, c, qa, qap, qb, qbp):
	"""
	claim c, with questions qa, qap for interface A, and ... for interface B
	"""

	# c  = before seeing predicted veracity
	# cp = after seeeing predicted veracity
	data['C' + str(c)]  = combine_ans(map(likert_int, data['Q{}_1'.format(qa)]),  map(likert_int, data['Q{}_1'.format(qb)]))
	data['Cp' + str(c)] = combine_ans(map(likert_int, data['Q{}_1'.format(qap)]), map(likert_int, data['Q{}_1'.format(qbp)]))


def process_data(data):
	process_claim(data, 1, 1, 2,  11, 12)
	process_claim(data, 2, 3, 4,  13, 14)
	process_claim(data, 3, 5, 6,  15, 16)
	process_claim(data, 4, 7, 8,  17, 18)
	process_claim(data, 5, 9, 10, 19, 20)

	data['gold1'] = 0 # 1
	data['gold2'] = 0 # 19
	data['gold3'] = 0 # 26
	data['gold4'] = 1 # 30
	data['gold5'] = 1 # 34

