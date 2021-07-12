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
            

# class Trajectory is used in the dataset
# for candidates, it is stored in the form of id(tuple)


class Trajectory():
    def __init__(self,data):
        self.data = np.array(data,dtype='int')
        self.data_length = len(data)

    def checkSub(self,query):
        if KMP_algorithm(self.data,query) == -1:
            return False
        return True

    def length(self):
        return self.data_length

    def __eq__(self,other):
        if self.data.shape != other.data.shape:
            return False
        comp = (self.data == other.data)
        return comp.all()

    def id(self):
        return tuple(self.data)


class SeqDataSet():
    def __init__(self,points):
        self.points = points
        self.record = []

    def add_line(self,line):
        self.record.append(line)
    
    def get_line(self,index):
        return self.record[index]

    def get_line_num(self):
        return len(self.record)

    def __getitem__(self,index):
        return self.get_line(index)

    def init_candidate(self):
        candidates = []
        for p in self.points:
            candi = tuple([p])
            candidates.append(candi)
        return candidates

class Itemset():
    def __init__(self,data):
        self.data = set(data)
        self.data_length = len(data)

    def checkSub(self,query):
        for i in query:
            if i not in self.data:
                return False
        return True

    def length(self):
        return self.data_length

    def __eq__(self,other):
        comp = (self.id() == other.id())
        return comp

    def id(self):
        return tuple(list(self.data).sort())

class ItemDataSet():
    def __init__(self,points):
        self.points = points
        self.record = []

    def add_line(self,line):
        self.record.append(line)
    
    def get_line(self,index):
        return self.record[index]

    def get_line_num(self):
        return len(self.record)

    def __getitem__(self,index):
        return self.get_line(index)

    def init_candidate(self):
        candidates = []
        for p in self.points:
            candi = tuple([p])
            candidates.append(candi)
        return candidates

class Hitterset():
    def __init__(self,data):
        self.data = set(data)
        self.data_length = len(data)

    def checkSub(self,query):
        if query in self.data:
            return True
        return False

    def length(self):
        return 1

    def __eq__(self,other):
        comp = (self.id() == other.id())
        return comp

    def id(self):
        return tuple(list(self.data).sort())

class HitterDataSet():
    def __init__(self,points):
        self.points = points
        self.record = []

    def add_line(self,line):
        self.record.append(line)
    
    def get_line(self,index):
        return self.record[index]

    def get_line_num(self):
        return len(self.record)

    def __getitem__(self,index):
        return self.get_line(index)

    def init_candidate(self):
        return self.points