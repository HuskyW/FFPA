# All inner structure of the server running FFPA
# It consists of three pools (candidate, admitted, rejected) and a candidate ganerator triggered by new admission of candidates

import numpy as np
from copy import deepcopy
import random
import math
from models.Apriori import seqUtils

class CandidatePool():
    def __init__(self,args):
        self.pool = {}
        self.eta = args.eta
        self.xi = args.xi
        self.k = args.k
        self.n = args.num_clients
        self.kprop = self.k/self.n

    def newCandidate(self,candidate):
        self.pool[candidate] = [0,0]

    def drawCandidate(self,num):
        keys = list(self.pool.keys())
        res = []
        while num > len(keys):
            res += keys.copy()
            num -= len(keys)
        idxs = np.random.choice(len(keys),num,replace=False)
        for idx in idxs:
            res.append(keys[idx])
        return res
        
    def updateResponse(self,candidate,res):
        # res:: 0: no; 1: yes
        self.pool[candidate][0] += res[0]
        self.pool[candidate][1] += res[1]
    
    def leaveCheck(self):
        accept = []
        reject = []

        removed = []
        for k in self.pool.keys():
            res = self.__supportCountBar(k)
            if res == 2:
                accept.append(k)
                removed.append(k)
            if res == 1:
                reject.append(k)
                removed.append(k)
        
        for k in removed:
            del self.pool[k]

        return accept, reject

    def __supportCountBar(self,candidate):
        # 0: retain; 1: reject; 2: accept
        yes = self.pool[candidate][1]
        no = self.pool[candidate][0]
        prop = yes / (yes + no)
        support = yes + no
        upper_thres = self.kprop * (1 - self.eta) + (1-self.kprop) * self.eta + math.sqrt(-math.log(self.xi)/(2*support) )
        lower_thres = self.kprop * (1 - self.eta) + (1-self.kprop) * self.eta - math.sqrt(-math.log(self.xi)/(2*support) )

        if prop > upper_thres:
            return 2
        if prop < lower_thres:
            return 1
        return 0

    def candidate_num(self):
        return len(self.pool.keys())

class AcceptPool():
    def __init__(self,utils):
        self.pool = {}
        self.utils = utils
        self.super_pool = {}

    def __inPool(self,target):
        l = self.utils.length(target)
        for comp in self.pool[l]:
            if comp == target:
                return True
        return False
    
    def __findCandidate(self,target):
        l = self.utils.length(target)
        target_pool = self.pool[l]
        new_candidates = set()
        for tail in target_pool:
            res1 = self.utils.linker(target,tail)
            res2 = self.utils.linker(tail,target)
            res = set()
            for i in res1:
                res.add(i)
            for i in res2:
                res.add(i)
            for res_candidate in res:
                subs = self.utils.sub(res_candidate)
                valid = 1
                for sub in subs:
                    if self.__inPool(sub) is False:
                        valid = 0
                        break
                if valid == 1:
                    new_candidates.add(res_candidate)
        return new_candidates

    def addAccept(self,target):
        l = self.utils.length(target)
        if l not in self.pool.keys():
            self.pool[l] = set()
            self.super_pool[l] = set()
        self.pool[l].add(target)
        self.super_pool[l].add(target)
        
        subs = self.utils.sub(target)
        for sub in subs:
            l_sub = self.utils.length(sub)
            self.super_pool[l_sub].discard(sub)

        new_candidates = self.__findCandidate(target)
        return new_candidates

    def __normalizePool(self,pool):
        res = set()
        for subpool in pool.values():
            res.update(subpool)
        return res
    
    def output(self):
        return self.__normalizePool(self.pool)

    def outputSuper(self):
        return self.__normalizePool(self.super_pool)


class FfpaServer():
    def __init__(self,args):
        self.args = args
        self.candidate_pool = CandidatePool(self.args)
        if self.args.pattern_type == 'sequence':
            utils = seqUtils()
        self.accept_pool = AcceptPool(utils)
    
    def drawCandidate(self,num):
        return self.candidate_pool.drawCandidate(num)

    def initCandidate(self,candidate):
        self.candidate_pool.newCandidate(candidate)
    
    def uploadSupportCount(self,update):
        for candidate, support in update.items():
            self.candidate_pool.updateResponse(candidate,support)
        accept, reject = self.candidate_pool.leaveCheck()
        new_candidates = set()
        for ac in accept:
            res = self.accept_pool.addAccept(ac)
            new_candidates.update(res)

        for new_c in new_candidates:
            self.candidate_pool.newCandidate(new_c)
        return accept, reject

    def candidateNum(self):
        return len(self.candidate_pool.pool.keys())
        
    def terminal(self):
        if self.candidateNum() == 0:
            return True
        return False

    def output(self):
        return self.accept_pool.output()
    