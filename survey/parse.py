import pandas as pd
import numpy as np

#data = pd.read_csv('Research+Study_March+8%2C+2018_15.56.csv')
#data = pd.read_csv('Research+Study_March+9%2C+2018_00.30.csv')

def likert_int(input_s):
    s = str(input_s)
    if s.lower() == 'definitely false':
        return 1
    elif s.lower() == 'probably false':
        return 2
    elif s.lower() == 'neutral':
        return 3
    elif s.lower() == 'probably true':
        return 4
    elif s.lower() == 'definitely true':
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
    
    data['E' + str(c)]  = data['gold' + str(c)] - data['C' + str(c)]
    data['Ep' + str(c)] = data['gold' + str(c)] - data['Cp' + str(c)]


def process_data(input_data):
    
    data = input_data.iloc[2:]
    
    data['gold1'] = 1 # 1
    data['gold2'] = 1 # 19
    data['gold3'] = 1 # 26
    data['gold4'] = 5 # 30
    data['gold5'] = 5 # 34
    data['golda'] = 3 # attention check
    
    process_claim(data, 1, 1, 2,  11, 12)
    process_claim(data, 2, 3, 4,  13, 14)
    process_claim(data, 3, 5, 6,  15, 16)
    process_claim(data, 4, 7, 8,  17, 18)
    process_claim(data, 5, 9, 10, 19, 20)
    process_claim(data, 'a', 47, 48, 46, 45)
    
    data['mean error'] = reduce(lambda x, y:x+y, [abs(data['E{}'.format(c)]) for c in [1,2,3,4,5] ]) / 5.0
    data['interface'] = ['A' if x==x  else 'B' for x in data['Q1_1']]
    
    return data

def get_loc(ip):
    import pygeoip
    GEOIP = pygeoip.GeoIP("GeoIP.dat", pygeoip.MEMORY_CACHE)
    return GEOIP.country_name_by_addr(ip)
    

def main():
    data = pd.read_csv('Research+Study_March+9%2C+2018_00.30.csv')
    d = process_data(data)
    d['loc'] = [get_loc(ip) for ip in d['IPAddress']]
    print np.mean(d['mean error'][d.interface == 'A'])
    print np.mean(d['mean error'][d.interface == 'B'])
    print d[['mean error', 'interface', 'Duration (in seconds)', 'loc']]
    
    
    
