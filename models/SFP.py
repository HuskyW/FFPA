'''
    Implementation of SFP algorithm proposed by Apple
    See https://machinelearning.apple.com/research/learning-with-privacy-at-scale for details
    Since the algorithm is too time-consuming, we only implement the multi-process version
'''
import hashlib
import multiprocess
import numpy as np
import math
import random

from models.Handlers import Handler
from utils.Sampling import sampleClients
import itertools

class SfpHandler(Handler):
    def __init__(self,args,dataset):
        self.args = args
        self.dataset = dataset
        self.fixed_traj_len = 6 # must be even and >= 4
        self.frag_option_num = int(self.fixed_traj_len/2)

        self.hash_size = 1024
        self.hash_num = 2048

        self.unique_hash_size = 256
        
        self.salts_a = [] # used as defining different hash functions
        self.salts_b = []
        self.salts_unique = 'unique'
        
        for i in range(self.hash_num):
            self.salts_a.append(str(i))
            self.salts_b.append(str(-i))

        self.epsilon_a = 0.25 * self.args.epsilon
        self.epsilon_b = self.args.epsilon - self.epsilon_a

        self.popular_threshold = self.args.sfp_threshold

        self.k_thres = (self.args.k * self.args.num_participants * self.args.k_cut) / (self.dataset.get_traj_num() * self.args.duplicate)

        if self.args.process <= 0:
            print('Our SFP implementation only works in multi-process')
            exit(0)
        
    def __tailerTraj(self,idx):
        '''
            Tailer the original trajectory into a fixed length
        '''
        traj = list(self.dataset[idx])
        if len(traj) == self.fixed_traj_len:
            return traj
        if len(traj) < self.fixed_traj_len:
            while len(traj) < self.fixed_traj_len:
                traj.append(-1)
            return traj
        head = np.random.randint(len(traj) - self.fixed_traj_len + 1)
        tailered = traj[head:head+self.fixed_traj_len]
        return tailered

    def __fixResLength(self,orig):
        '''
            Cut the fragments to what we want, and remove thoes with paddings
        '''
        res = []
        for candi in orig:
            for i in range(len(candi) - self.args.l + 1):
                cutted = tuple(candi[i:i+self.args.l])
                if -1 in set(cutted):
                    continue
                res.append(cutted)
        return list(set(res))

    def __hashA(self,data,hash_idx):
        '''
            Hash for the original data
        '''
        h = hashlib.sha256()
        h.update(self.salts_a[hash_idx].encode('utf-8') + data.encode('utf-8'))
        res = int.from_bytes(h.digest(),'big')
        return res % self.hash_size

    def __hashB(self,data,hash_idx):
        '''
            Hash for the merged data (oracle)
        '''
        h = hashlib.sha256()
        h.update(self.salts_b[hash_idx].encode('utf-8') + data.encode('utf-8'))
        res = int.from_bytes(h.digest(),'big')
        return res % self.hash_size

    def __hashUnique(self,data):
        '''
            Hash for the rest part of merged data (oracle)
        '''
        h = hashlib.sha256()
        h.update(self.salts_unique.encode('utf-8') + data.encode('utf-8'))
        res = int.from_bytes(h.digest(),'big')
        return res % self.unique_hash_size

    def __noisyMatrix(self,epsilon):
        '''
            a noisy matrix of -1 and 1
        '''
        possi = (math.e**(epsilon / 2.0)) / (math.e**(epsilon / 2.0) + 1.0)
        res = np.zeros(self.hash_size,dtype='float')
        for i in range(self.hash_size):
            if np.random.rand() < possi:
                res[i] = 1
            else:
                res[i] = -1
        return res

    def __cEpsilon(self,epsilon):
        top = math.e ** (epsilon/2.0) + 1.0
        bottom = math.e ** (epsilon/2.0) - 1.0
        res = top/(2.0 * bottom)
        return res
    
    def __noisyRowMatrix(self,target_idx,epsilon):
        '''
            Complete the noisy response
        '''
        basis = -1 * np.ones(self.hash_size,dtype='float')
        basis[target_idx] = 1
        noise = self.__noisyMatrix(epsilon)
        multiplied = np.multiply(basis,noise)
        c_ep = self.__cEpsilon(epsilon)
        multiplied = c_ep * multiplied
        multiplied = multiplied + 0.5
        multiplied = self.hash_size * multiplied
        return multiplied

    def __clientHashOracle(self,traj):
        '''
            Oracle hashing results
        '''
        hash_idx = np.random.randint(self.hash_num)
        l = random.randrange(0,self.fixed_traj_len-1,2)
        unique_hash = self.__hashUnique(str(traj))
        tempres = str(unique_hash) + str(traj[l:l+2])
        final_hash = self.__hashB(tempres,hash_idx)
        return final_hash, hash_idx, l

    def __clientHashMain(self,traj):
        '''
            Original hashing results
        '''
        hash_idx = np.random.randint(self.hash_num)
        return self.__hashA(str(traj),hash_idx), hash_idx

    def __clientResponse(self,idx):
        '''
            All encoding works for a client
        '''
        traj = self.__tailerTraj(idx)
        a_res, a_hashidx = self.__clientHashMain(traj)
        b_res, b_hashidx, l = self.__clientHashOracle(traj)
        a_resmatrix = self.__noisyRowMatrix(a_res,self.epsilon_a)
        b_resmatrix = self.__noisyRowMatrix(b_res,self.epsilon_b)
        return a_resmatrix, b_resmatrix, a_hashidx, b_hashidx, l

    def __initCms(self):
        a_cms = []
        for i in range(self.hash_num):
            a_cms.append(np.zeros(self.hash_size,dtype='float'))
        b_cms = []
        for i in range(self.frag_option_num):
            b_cms.append([])
        for i in range(self.frag_option_num):
            for j in range(self.hash_num):
                b_cms[i].append(np.zeros(self.hash_size,dtype='float'))
        return a_cms, b_cms

    def __clientWorker(self,participents,queue,proc_idx):
        a_cms, b_cms = self.__initCms()
        num_milestone = 5
        milestone = math.floor(len(participents)/num_milestone)
        for idx in range(len(participents)):
            if idx > 0 and idx % milestone == 0 and int(idx/milestone) != num_milestone and self.args.verbose:
                print("Worker %2d: %d%% done" % (proc_idx,int(round(idx*100/len(participents)))))
            client_idx = participents[idx]
            a_resmatrix, b_resmatrix, a_hashidx, b_hashidx, l = self.__clientResponse(client_idx)
            a_cms[int(a_hashidx)] += a_resmatrix
            b_cms[int(l/2)][b_hashidx] += b_resmatrix
        queue.put([a_cms,b_cms])
        if self.args.verbose:
            print("Worker %2d: all done" % proc_idx)
        return
    
    def __estimateFeq(self,cms,target,which_cms): #which_cms? 0:a, 1:b
        if which_cms == 0:
            func = self.__hashA
        else:
            func = self.__hashB
        
        f = 0.0
        for i in range(self.hash_num):
            targetIdx = func(target,i)
            f += cms[i][targetIdx]
        f /= self.hash_num
        f = ( self.hash_size/(self.hash_size-1) ) * ( f- self.args.num_participants/self.hash_size )
        return f

    def __allPossibleFragments(self):
        '''
            possible fragments with length 2 at all possible location
        '''
        res = []
        for loc in range(self.frag_option_num):
            for i in range(-1,self.dataset.location_num):
                for j in range(-1,self.dataset.location_num):
                    res.append((loc,i,j))
        return res

    def __estimateOracleWorker(self,b_cms,workload,queue,proc_idx):
        estimates = {}
        num_milestone = 5
        milestone = math.floor(len(workload)/num_milestone)
        for idx in range(len(workload)):
            if idx > 0 and idx % milestone == 0 and int(idx/milestone) != num_milestone and self.args.verbose:
                print("Worker %2d: %d%% done" % (proc_idx,int(round(idx*100/len(workload)))))
            candidate = workload[idx]
            loc = candidate[0]
            target_frag = [candidate[1],candidate[2]]
            f = -float('inf')
            for i in range(self.unique_hash_size):
                target = str(i) + str(target_frag)
                f_est = self.__estimateFeq(b_cms[loc],target,1)
                f = max(f,f_est)
            estimates[candidate] = f
        queue.put(estimates)
        if self.args.verbose:
            print("Worker %2d: all done" % proc_idx)
        return

    def __finalCheckWorker(self,a_cms,workload,queue,proc_idx):
        passed = []
        num_milestone = 5
        milestone = math.floor(len(workload)/num_milestone)
        for idx in range(len(workload)):
            if idx > 0 and idx % milestone == 0 and int(idx/milestone) != num_milestone and self.args.verbose:
                print("Worker %2d: %d%% done" % (proc_idx,int(round(idx*100/len(workload)))))
            candidate = workload[idx]
            f = self.__estimateFeq(a_cms,str(candidate),0)
            if f >= self.k_thres:
                passed.append(candidate)
        queue.put(passed)
        if self.args.verbose:
            print("Worker %2d: all done" % proc_idx)
        return


    def run(self):
        participents = sampleClients(self.args,self.dataset.get_traj_num(),self.args.num_participants)
        a_cms, b_cms = self.__initCms()
        mananger = multiprocess.Manager()
        queue = mananger.Queue()
        jobs = []
        workload = math.floor(len(participents)/self.args.process)
        print("Receiving client info...")
        for proc_idx in range(self.args.process):
            if proc_idx == self.args.process - 1:
                participents_load = participents[proc_idx*workload:len(participents)]
            else:
                participents_load = participents[proc_idx*workload:(proc_idx+1)*workload]
            
            p = multiprocess.Process(target=self.__clientWorker,args=(participents_load,queue,proc_idx))
            jobs.append(p)
            p.start()

        for p in jobs:
            p.join()


        print("Aggregating cms...")

        results = [queue.get() for j in jobs]
        for res in results:
            a_res = res[0]
            b_res = res[1]

            for i in range(self.hash_num):
                a_cms[i] += a_res[i]
            for i in range(self.frag_option_num):
                for j in range(self.hash_num):
                    b_cms[i][j] += b_res[i][j]

        print("Estimating fragments...")
        possible_fragments = self.__allPossibleFragments()
        mananger = multiprocess.Manager()
        queue = mananger.Queue()
        jobs = []
    
        workload = math.floor(len(possible_fragments)/self.args.process)
        for proc_idx in range(self.args.process):
            if proc_idx == self.args.process - 1:
                process_load = possible_fragments[proc_idx*workload:len(participents)]
            else:
                process_load = possible_fragments[proc_idx*workload:(proc_idx+1)*workload]
            
            p = multiprocess.Process(target=self.__estimateOracleWorker,args=(b_cms,process_load,queue,proc_idx))
            jobs.append(p)
            p.start()

        for p in jobs:
            p.join()

        print("Aggregating oracles...")

        results = [queue.get() for j in jobs]
        oracles = []
        for i in range(self.frag_option_num):
            oracles.append({})
        for res in results:
            for key, value in res.items():
                loc = key[0]
                frag = (key[1],key[2])
                oracles[loc][frag] = value
        
        popular_frags = []
        for i in range(self.frag_option_num):
            popular_frags.append([])
        for i in range(self.frag_option_num):
            oracle = oracles[i]
            oracle_sorted = sorted(oracle.items(),key=lambda item:item[1],reverse=True)
            for j in range(min(self.popular_threshold,len(oracle_sorted))):
                popular_frags[i].append(tuple(oracle_sorted[j][0]))

        merged_candidates = []
        for target in itertools.product(*popular_frags):
            temp = []
            for i in range(len(target)):
                temp.extend(list(target[i]))
            merged_candidates.append(temp)
        
        print('Merged candidate generated: %d' % len(merged_candidates))
        print('Final checking...')
        mananger = multiprocess.Manager()
        queue = mananger.Queue()
        jobs = []
        workload = math.floor(len(merged_candidates)/self.args.process)
        for proc_idx in range(self.args.process):
            if proc_idx == self.args.process - 1:
                process_load = merged_candidates[proc_idx*workload:len(merged_candidates)]
            else:
                process_load = merged_candidates[proc_idx*workload:(proc_idx+1)*workload]
            
            p = multiprocess.Process(target=self.__finalCheckWorker,args=(a_cms,process_load,queue,proc_idx))
            jobs.append(p)
            p.start()

        for p in jobs:
            p.join()

        results = [queue.get() for j in jobs]
        
        desired = []
        for res in results:
            desired.extend(res)
        
        print('Final checking complete: %d' % len(desired))

        cutted = self.__fixResLength(desired)
        print('Target fragment found: %d' % len(cutted))

        return cutted

    def test(self):
        a_cms,b_cms = self.__initCms()
        for i in range(100000):
            a_resmatrix, b_resmatrix, a_hashidx, b_hashidx, l = self.__clientResponse(0)
            b_cms[int(l/2)][b_hashidx] += b_resmatrix
            a_cms[a_hashidx] += a_resmatrix
        
        
        for i in range(self.unique_hash_size):
            target = str(i) + str([1,4])
            f = self.__estimateFeq(b_cms[0],target,1)
            print(f)
        
        target = [1,4,7,8,3,5]
        f = self.__estimateFeq(a_cms,str(target),0)
        print(f)
        return



