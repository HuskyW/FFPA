import numpy as np
from copy import deepcopy
import random

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

        random.shuffle(self.candidates)

        self.idx = self.idx + num - len(self.candidates)
        res.extend(self.candidates[0:self.idx])
        return res

def sampleClients(args,orig_traj_num,m):
    clients = []
    for i in range(args.duplicate):
        clients.extend(list(range(orig_traj_num)))

    res = np.random.choice(clients,m,replace=False)
    return res