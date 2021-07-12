# All inner structure of the server running FFPA
# It consists of three pools (candidate, admitted, rejected) and a candidate ganerator triggered by new admission of candidates

import numpy as np
from copy import deepcopy
import random
import math
from models.Apriori import *

class CandidatePool():
    def __init__(self,args):
        self.pool = {}
        self.args = args
        self.kprop = self.args.k/self.args.num_clients
        self.leave_log = {} # how many support got when leaving the pool

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
            self.leave_log[k] = self.pool[k][0] + self.pool[k][1]
            del self.pool[k]

        return accept, reject

    def __supportCountBar(self,candidate):
        # 0: retain; 1: reject; 2: accept
        yes = self.pool[candidate][1]
        no = self.pool[candidate][0]
        support = yes + no
        if support == 0:
            return 0
        prop = yes / support
        upper_thres = self.kprop * (1 - self.args.eta) + (1-self.kprop) * self.args.eta + math.sqrt(-math.log(self.args.xi)/(2*support) )
        lower_thres = self.kprop * (1 - self.args.eta) + (1-self.kprop) * self.args.eta - math.sqrt(-math.log(self.args.xi)/(2*support) )
        middle_thres = self.kprop * (1 - self.args.eta) + (1-self.kprop) * self.args.eta

        if self.args.max_support > 0 and support > self.args.max_support:
            if prop > middle_thres:
                return 2
            return 1

        if prop > upper_thres:
            return 2
        if prop < lower_thres:
            return 1
        return 0

    def candidate_num(self):
        return len(self.pool.keys())

    def get_leave_log(self):
        return self.leave_log

class AcceptPool():
    def __init__(self,utils):
        self.pool = {}
        self.utils = utils
        self.super_pool = {}
        self.candidate_history = set()

    def __inPool(self,target):
        l = self.utils.length(target)
        for comp in self.pool[l]:
            if comp == target:
                return True
        return False
    
    def __findCandidate(self,l):
        target_pool = self.pool[l]
        new_candidates = set()
        for head in target_pool:
            for tail in target_pool:
                res1 = self.utils.linker(head,tail)
                res2 = self.utils.linker(tail,head)
                res = set()
                for i in res1:
                    if i not in self.candidate_history:
                        res.add(i)
                for i in res2:
                    if i not in self.candidate_history:
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

    def addAccept(self,accepts):
        focus_len = set()
        for ac in accepts:
            l = self.utils.length(ac)
            focus_len.add(l)
            if l not in self.pool.keys():
                self.pool[l] = set()
                self.super_pool[l] = set()
            self.pool[l].add(ac)
            self.super_pool[l].add(ac)
        
            subs = self.utils.sub(ac)
            for sub in subs:
                l_sub = self.utils.length(sub)
                self.super_pool[l_sub].discard(sub)

        new_candidates = set()
        for l in focus_len:
            new_candidates.update(self.__findCandidate(l))
        for candi in new_candidates:
            self.candidate_history.add(candi)
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
        elif self.args.pattern_type == 'itemset':
            utils = itemUtils()
        elif self.args.pattern_type == 'item':
            utils = hitterUtils()
        self.accept_pool = AcceptPool(utils)
    
    def drawCandidate(self,num):
        return self.candidate_pool.drawCandidate(num)

    def initCandidate(self,candidate):
        self.candidate_pool.newCandidate(candidate)
    
    def uploadSupportCount(self,update):
        for candidate, support in update.items():
            self.candidate_pool.updateResponse(candidate,support)
        accept, reject = self.candidate_pool.leaveCheck()
        res = self.accept_pool.addAccept(accept)
        new_candidates = set(res)
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

    def getLeaveLog(self):
        return self.candidate_pool.get_leave_log()
    