import numpy as np
import random

def gen_pnext(substring):
    index, m = 0, len(substring)
    pnext = [0]*m
    i = 1
    while i < m:
        if (substring[i] == substring[index]):
            pnext[i] = index + 1
            index += 1
            i += 1
        elif (index!=0):
            index = pnext[index-1]
        else:
            pnext[i] = 0
            i += 1
    return pnext

def KMP_algorithm(string, substring):
    pnext = gen_pnext(substring)
    n = len(string)
    m = len(substring)
    i, j = 0, 0
    while (i<n) and (j<m):
        if (string[i]==substring[j]):
            i += 1
            j += 1
        elif (j!=0):
            j = pnext[j-1]
        else:
            i += 1
    if (j == m):
        return i-j
    else:
        return -1
            


class Trajectory():
    # One trajectory record
    def __init__(self,data):
        self.data = np.array(data,dtype='int')
        self.data_length = len(data)
    
    def uploadOne(self):
        return random.choice(self.data)

    def checkSubSeq(self,query):
        if KMP_algorithm(self.data,query) == -1:
            return 0
        return 1

    def randomFragment(self,fragment_length):
        index = np.random.randint(self.data_length-fragment_length)
        return self.data[index:index+fragment_length]

class DataSet():
    def __init__(self,location_num):
        self.location_num = location_num
        self.record = []

    def add_trajectory(self,trajectory):
        self.record.append(trajectory)
    
    def get_trajectory(self,index):
        return self.record[index]