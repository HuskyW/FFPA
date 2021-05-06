'''
    Representation of trajectory and corresponding dataset in our work
'''

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
            return False
        return True

    def randomFragment(self,fragment_length):
        index = np.random.randint(self.data_length-fragment_length)
        return self.data[index:index+fragment_length]

    def allLocations(self):
        return set(self.data)

    def spellData(self):
        print(list(self.data))

class DataSet():
    def __init__(self,location_num):
        self.location_num = location_num
        self.record = []

    def add_trajectory(self,trajectory):
        self.record.append(np.array(trajectory,dtype='int'))
    
    def get_trajectory(self,index):
        return self.record[index]

    def get_traj_num(self):
        return len(self.record)

    def __getitem__(self,index):
        return self.get_trajectory(index)
    
    def uploadOne(self,idx):
        return random.choice(self.record[idx])

    def checkSubSeq(self,idx,query):
        if KMP_algorithm(self.record[idx],query) == -1:
            return False
        return True

    def randomFragment(self,idx,fragment_length):
        index = np.random.randint(len(self.record[idx])-fragment_length)
        return self.record[idx][index:index+fragment_length]

    def allLocations(self,idx):
        return set(self.record[idx])