import math
import multiprocess
import numpy as np
import itertools

from utils.Sampling import sampleClients
from models.Handlers import Handler
from models.Randomize import Randomizer


class RapporHandler(Handler):
    def __init__(self,args,dataset):
        self.args = args
        self.dataset = dataset
        self.args.eta = 1 / (math.e**(self.args.epsilon / 2.0) + 1.0)
        self.orig_rec_num = self.dataset.get_line_num()
        self.clients_num = self.orig_rec_num * self.args.duplicate
        self.args.num_clients = self.clients_num
        self.randomizer = Randomizer(self.args)
        self.num_points = len(self.dataset.points)
        self.one_hot_size = 2 ** self.num_points
        if self.args.pattern_type != "itemset":
            print("Error: rappor can only work for itemset datasets")
            exit(0)


    def __data2idx(self,data):
        res = 0
        for i in data:
            res += (2**i)
        return res

    def __idx2data(self,idx):
        res = []
        nextitem = 0
        while idx > 0:
            if idx % 2 == 1:
                res.append(nextitem)
            idx = math.floor(idx/2)
            nextitem += 1
        return tuple(res)

    def __oneClient(self,client_idx):
            raw_data = self.dataset[client_idx].data
            data_idx = self.__data2idx(raw_data)
            res = np.zeros(self.one_hot_size,dtype='int')
            res[data_idx] = 1
            res = self.randomizer.randomBits(res)
            return res

    def __processWorker(self,proc_idx,participents,queue):
        support = np.zeros(self.one_hot_size,dtype='int')
        num_milestone = 5
        milestone = math.floor(len(participents)/num_milestone)
        for idx in range(len(participents)):
            if idx > 0 and idx % milestone == 0 and int(idx/milestone) != num_milestone and self.args.verbose:
                print("Worker %2d: %d%% done" % (proc_idx,int(round(idx*100/len(participents)))))
            client_idx = participents[idx]
            res = self.__oneClient(client_idx)
            support += res
        queue.put(support)
        return

    def __allsubs(self,target):
        l_target = len(target)
        res = set()
        for l in range(1,l_target+1):
            for subset in itertools.combinations(list(target),l):
                subset = list(subset)
                subset.sort()
                res.add(tuple(subset))
        return res

    def __supportthres(self):
        targetFreq = self.args.k / self.clients_num
        noisyFreq = (1-self.args.eta) * targetFreq + self.args.eta * (1-targetFreq)
        return self.args.num_participants * noisyFreq



    def run(self):
        participents = sampleClients(self.args,self.orig_rec_num)
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

        support_count = np.zeros(self.one_hot_size,dtype='int')
        for res in results:
            support_count += res

        fragments = set()
        support_thres = self.__supportthres()
        for i in range(self.one_hot_size):
            if support_count[i] >= support_thres:
                good_frag = self.__idx2data(i)
                allsub = self.__allsubs(good_frag)
                fragments.update(allsub)

        return fragments
