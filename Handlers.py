'''
    Handler of FastPub, an FastPubHandler instance an do all works of trajectory publication given the dataset
'''
import abc
from utils.Randomize import *
import math
import numpy as np
from collections import defaultdict
from models.Candidate import generateCandidates
from utils.Sampling import CandidateSampler, sampleClients
from utils.Print import printRound
import multiprocess


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
        self.c_len = [0] * self.args.l


    def __calculateEtaRoundOne(self):
        epsilon = self.args.epsilon
        a = math.pow(math.e,epsilon)/(self.loc_num-1)
        return 1/(a+1)

    def __calculateEtaLonger(self):
        epsilon = self.args.epsilon
        return 1/(1 + math.pow(math.e,(epsilon/self.c_len[self.round])))

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
    
    def later_round(self,traj,candidates):
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
    
    def later_round_worker(self,process_idx,candidates,participents,queue):
        num_milestone = 5
        milestone = math.floor(len(participents)/num_milestone)
        local_support_count = defaultdict(lambda : 0)
        sampler = CandidateSampler(candidates)
        for idx in range(len(participents)):
            if idx > 0 and idx % milestone == 0 and self.args.verbose:
                print("Worker %2d: %d%% done" % (process_idx,int(round(idx*100/len(participents)))))
            
            client_idx = participents[idx]
            traj = self.dataset.get_trajectory(client_idx)
            candis = sampler.sample(self.c_len[self.round])
            res = self.later_round(traj,candis)

            for key,value in res.items():
                local_support_count[key] += value

        queue.put(local_support_count)
        if self.args.verbose:
            print("Worker %2d: all done" % process_idx)
        return


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
        printRound(1)
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
            printRound(fragment_len+1)
            self.round += 1
            candidates = generateCandidates(fragments)
            print("%d-fragments: %d candidates" % (fragment_len+1,len(candidates)))
            if len(candidates) == 0:
                print('No candidate with length ' + str(fragment_len+1))
                return None

            self.c_len[self.round] = min(self.args.c_max,len(candidates))
            self.eta[fragment_len] = self.__calculateEtaLonger()

            sampler = CandidateSampler(candidates)

            participents = sampleClients(clients_num,self.args.num_participants)

            support_count = defaultdict(lambda : 0)
            
                
            if self.args.process <= 0:
                for idx in range(len(participents)):
                    if idx % 100000 == 0 and idx > 0 and self.args.verbose:
                        print("%d trajectories checked" % idx)
                    client_idx = participents[idx]
                    traj = self.dataset.get_trajectory(client_idx)
                    candis = sampler.sample(self.c_len[self.round])
                    res = self.later_round(traj,candis)
                    for key,value in res.items():
                        support_count[key] += value
            else:
                mananger = multiprocess.Manager()
                queue = mananger.Queue()
                jobs = []
                workload = math.floor(len(participents)/self.args.process)
                for proc_idx in range(self.args.process):
                    if proc_idx == self.args.process - 1:
                        participents_load = participents[proc_idx*workload:len(participents)]
                    else:
                        participents_load = participents[proc_idx*workload:(proc_idx+1)*workload]
                    p = multiprocess.Process(target=self.later_round_worker,args=(proc_idx,candidates,participents_load,queue))
                    jobs.append(p)
                    p.start()

                for p in jobs:
                    p.join()
                
                if self.args.verbose:
                    print("Aggregating...")

                results = [queue.get() for j in jobs]

                for res in results:
                    for key,value in res.items():
                        support_count[key] += value



                

            query_per_candi = self.args.num_participants * self.c_len[self.round] /len(candidates)
            print("Candidate avg chance: %.2f" % query_per_candi)
            self.thres[fragment_len] = self.__calculateThresLonger(query_per_candi)

            fragments = self.__filterCandidates(support_count)


            print("eta: %.3f" % self.eta[fragment_len])
            print("thres: %.2f" % self.thres[fragment_len])
            print("%d-fragments: %d admitted" % (fragment_len+1,len(fragments)))
        return fragments
                
                





