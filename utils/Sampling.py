import numpy as np
from copy import deepcopy

class CandidateSampler():
    def __init__(self,candidates):
        self.candidates = list(candidates)
        self.idx = 0
    
    def sample(self,num):
        if num > len(self.candidates):
            print("candidate sampling error")
            exit(0)
        if self.idx + num <= len(self.candidates):
            res = self.candidates[self.idx:self.idx+num]
            self.idx += num
            return res
        res = self.candidates[self.idx:len(self.candidates)]
        self.idx = self.idx + num - len(self.candidates)
        res.extend(self.candidates[0:self.idx])
        return res

def sampleClients(n_client,m):
    res = []
    clients = list(range(n_client))
    m_left = m
    while m_left > n_client:
        res.extend(deepcopy(clients))
        m_left -= n_client

    res.extend(np.random.choice(clients,m_left,replace=False))
    return res