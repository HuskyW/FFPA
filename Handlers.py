import abc
from utils.Randomize import *
import math
import numpy as np
from collections import defaultdict
from models.Candidate import generateCandidates
from utils.Sampling import CandidateSampler, sampleClients




class Handler(metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def run(self):
        pass


class FastPubHandler(Handler):
    def __init__(self,args,dataset):
        self.args = args
        self.dataset = dataset
        self.clients_num = self.dataset.get_traj_num()
        self.loc_num = self.dataset.location_num
        self.round = 0
        self.eta = [0] * self.args.l
        self.thres = [0] * self.args.l


    def __calculateEtaRoundOne(self):
        epsilon = self.args.epsilon
        a = math.pow(math.e,epsilon)/(self.loc_num-1)
        return 1/(a+1)

    def __calculateEtaLonger(self,c_len):
        epsilon = self.args.epsilon
        return 1/(1 + math.pow(math.e,(epsilon/c_len)))

    def __calculateThresRoundOne(self):
        p_softk = self.args.k/self.clients_num
        p1 = (self.args.k/self.clients_num)*(1-self.eta[0])
        p2 = ((self.clients_num-self.args.k)/self.clients_num) * (self.eta[0]/(self.loc_num-1))
        p3 = math.sqrt(-math.log(self.args.xi)/(2*self.args.num_participants))

        p_softk = self.args.k/self.clients_num
        if self.args.softk:
            return self.args.num_participants*(p_softk+p3)

        return self.args.num_participants*(p1+p2+p3)

    def __calculateThresLonger(self,m): # m is times to be checked for each candidate
        p1 = (self.args.k/self.clients_num)*(1-self.eta[self.round])
        p2 = ((self.clients_num-self.args.k)/self.clients_num) * self.eta[self.round]
        p3 = math.sqrt(-math.log(self.args.xi)/(2*m))
        p_softk = self.args.k/self.clients_num
        
        if self.args.softk is False:
            return m*(p1+p2+p3)

        if self.round == self.args.l-1:
            return m*(p1+p2+p3)

        return m*(p_softk+p3)     

    def __first_round(self,traj):
        real_result = traj.uploadOne()
        noisy_result = randomInt(real_result,self.eta[0],self.loc_num)
        return noisy_result
    
    def __later_round(self,traj,candidates):
        candi_len = len(candidates)
        candi_save = list(candidates)
        response = [0] * candi_len
        for i in range(len(candidates)):
            if traj.checkSubSeq(candi_save[i]) is True:
                response[i] = 1
        response = randomBits(response,self.eta[self.round])
        final_response = {}
        for i in range(len(candidates)):
            final_response[candi_save[i]] = response[i]
        return final_response

    def __filterCandidates(self,support_count):
        exceed_k = [key for key,value in support_count.items() if value >= self.thres[self.round]]
        if self.args.admit_threshold < 0 or len(exceed_k) < self.args.admit_threshold:
            return exceed_k
        sc_sorted = sorted(support_count.items(),key=lambda item:item[1],reverse=True)
        res = []
        for i in range(self.args.admit_threshold):
            res.append(sc_sorted[i][0])
        return res
        
        

    def run(self):
        clients_num = self.dataset.get_traj_num()
        # publish 1-fragments
        self.eta[0] = self.__calculateEtaRoundOne()
        self.thres[0] = self.__calculateThresRoundOne()
        print("eta: %f" % self.eta[0])
        print("thres: %f" % self.thres[0])
        participents = sampleClients(clients_num,self.args.num_participants)

        support_count = defaultdict(lambda : 0)
        for client_idx in participents:
            traj = self.dataset.get_trajectory(client_idx)
            res = self.__first_round(traj)
            support_count[(res,)] += 1
        fragments = self.__filterCandidates(support_count)

        # publish longer fragments
        for fragment_len in range(1,self.args.l):
            self.round += 1
            candidates = generateCandidates(fragments)
            if self.args.verbose:
                print("%d-fragments: %d candidates" % (fragment_len+1,len(candidates)))
            if len(candidates) == 0:
                print('No candidate with length ' + str(fragment_len+1))
                return None

            c_len = min(self.args.c_max,len(candidates))
            self.eta[fragment_len] = self.__calculateEtaLonger(c_len)

            sampler = CandidateSampler(candidates)

            participents = sampleClients(clients_num,self.args.num_participants)

            done = 0
            support_count = defaultdict(lambda : 0)
            for client_idx in participents: 
                done += 1
                if done % 100000 == 0 and self.args.verbose:
                    print("%d trajectories checked" % done)
                traj = self.dataset.get_trajectory(client_idx)
                candis = sampler.sample(c_len)
                res = self.__later_round(traj,candis)
                for key,value in res.items():
                    support_count[key] += value

            query_per_candi = self.args.num_participants * c_len /len(candidates)
            print("Candidate avg chance: %.2f" % query_per_candi)
            self.thres[fragment_len] = self.__calculateThresLonger(query_per_candi)

            fragments = self.__filterCandidates(support_count)

            if self.args.verbose:
                print("eta: %.3f" % self.eta[fragment_len])
                print("thres: %.2f" % self.thres[fragment_len])
            
            if self.args.verbose:
                print("%d-fragments: %d admitted" % (fragment_len+1,len(fragments)))
        return fragments
                
                





