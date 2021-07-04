'''
    Handler of FFPA
'''
import abc
import math
import numpy as np
import multiprocess
import pickle
from collections import defaultdict


from utils.Sampling import sampleClients
from utils.Print import printRound, printLines
from models.Sandwich import FfpaServer
from models.Randomize import Randomizer
from utils.Naming import *

def logCandidateNum(args,candidate_log):
    path = CandidateDriftName(args)
    record = printLines(candidate_log)
    with open(path,'w') as fp:
        fp.write(record)

def logSupportNum(args,support_log):
    path = LeaveNumPickleName(args)
    with open(path,'wb') as fp:
        pickle.dump(support_log,fp)


class Handler(metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def run(self):
        pass


class FfpaHandler(Handler):
    def __init__(self,args,dataset):
        self.args = args
        self.args.eta = self.__calculateEta()
        self.dataset = dataset
        self.orig_rec_num = self.dataset.get_line_num()
        self.clients_num = self.orig_rec_num * self.args.duplicate
        self.args.num_clients = self.clients_num
        self.server = FfpaServer(self.args)
        self.randomizer = Randomizer(self.args)
        init_candidates = self.dataset.init_candidate()
        for candi in init_candidates:
            self.server.initCandidate(candi)

        self.round = 0

    def __calculateEta(self):
        epsilon = self.args.epsilon
        candidates = self.args.num_candidate
        return 1/(1 + math.pow(math.e,(epsilon/candidates)))


    def __oneClient(self,client_idx,candidates):
        candi_len = len(candidates)
        candi_save = list(candidates)
        response = [0] * candi_len
        for i in range(len(candidates)):
            if self.dataset[client_idx].checkSub(candi_save[i]) is True:
                response[i] = 1
        response = self.randomizer.randomBits(response)
        final_response = {}
        for i in range(len(candidates)):
            final_response[candi_save[i]] = response[i]
        return final_response


    def __processWorker(self,proc_idx,participents,queue):     
        support_count = defaultdict(lambda : 0)
        for idx in range(len(participents)):
            client_idx = participents[idx]
            candidates = self.server.drawCandidate(self.args.num_candidate)
            res = self.__oneClient(client_idx,candidates)
            for key,value in res.items():
                if key not in support_count.keys():
                    support_count[key] = [0,0]
                support_count[key][value] += 1

        queue.put(support_count)
        return



    def run(self):
        candidate_num_log = []
        while True:
            if self.server.terminal() is True:
                print('Terminal')

                if self.args.log_detail is True:
                    logCandidateNum(self.args,candidate_num_log)
                    logSupportNum(self.args,self.server.getLeaveLog())
                self.args.round = self.round
                return self.server.accept_pool.output()
            self.round += 1
            printRound(self.round)
            print("Candidate left: %d" % self.server.candidateNum())
            candidate_num_log.append(self.server.candidateNum())
            participents = sampleClients(self.args,self.orig_rec_num)

            support_count = defaultdict(lambda : 0)

            mananger = multiprocess.Manager()
            queue = mananger.Queue()
            jobs = []
            workload = math.floor(len(participents)/self.args.process)

            for proc_idx in range(self.args.process):
                if proc_idx == self.args.process - 1:
                    participents_load = participents[proc_idx*workload:len(participents)]
                else:
                    participents_load = participents[proc_idx*workload:(proc_idx+1)*workload]
                p = multiprocess.Process(target=self.__processWorker,args=(proc_idx,participents_load,queue))
                jobs.append(p)
                p.start()

            for p in jobs:
                p.join()


            results = [queue.get() for j in jobs]

            for res in results:
                for key,value in res.items():
                    if key not in support_count.keys():
                        support_count[key] = [0,0]
                    support_count[key][0] += value[0]
                    support_count[key][1] += value[1]
        
            
            accept, reject = self.server.uploadSupportCount(support_count)

            print("Accept: %d; Reject: %d" % (len(accept),len(reject)))

                





