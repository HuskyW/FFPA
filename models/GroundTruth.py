'''
    Calculate ground truth with standard Apriori algorithm
'''

from collections import defaultdict
from models.DataSet import SeqDataSet,Trajectory
from utils.Naming import SupportCountPickleName
import pickle
import multiprocess
import math
from utils.Print import printRound
from models.Apriori import *


def generateCandidates(fragment,util):
    res = []
    for a in fragment:
        for b in fragment:
            link = util.linker(a,b)
            allowed = []
            for li in link:
                flag = True
                subs = util.sub(li)
                for s in subs:
                    if s not in fragment:
                        flag = False
                        break
                if flag is True:
                    allowed.append(li)
            res += allowed
    return res


def ground_truth_worker(dataset,process_idx,candidates,participents,queue,verbose):
    num_milestone = 5
    milestone = math.floor(len(participents)/num_milestone)
    local_support_count = defaultdict(lambda : 0)
    for idx in range(len(participents)):
        if idx > 0 and idx % milestone == 0 and verbose:
            print("Worker %2d: %d%% done" % (process_idx,int(round(idx*100/len(participents)))))
        client_idx = participents[idx]
        for candi in candidates:
            if dataset[client_idx].checkSub(candi) is True:
                local_support_count[candi] += 1

    queue.put(local_support_count)
    if verbose:
        print("Worker %2d: all done" % process_idx)
    return

def groundTruth(dataset,args):
    if args.pattern_type == 'sequence':
        util = seqUtils()
    elif args.pattern_type == 'itemset':
        util = itemUtils()
    elif args.pattern_type == 'item':
        util = hitterUtils()
    k = int(args.k/args.duplicate)
    traj_num = dataset.get_line_num()
    frag_len = 0
    res = {}
    # longer fragments
    while True:
        frag_len += 1
        printRound(frag_len)
        if frag_len == 1:
            candidates = dataset.init_candidate()
        else:
            candidates = generateCandidates(fragments,util)
        print("%d-fragments: %d candidates" % (frag_len,len(candidates)))

        if len(candidates) == 0:
            print('Terminal')
            return res
        
        support_count = defaultdict(lambda : 0)
        if args.process <= 0:
            for traj_idx in range(traj_num):
                traj = dataset.get_trajectory(traj_idx)
                for candi in candidates:
                    if traj.checkSubSeq(candi) is True:
                        support_count[candi] += 1

                if traj_idx % 10000 == 0 and args.verbose:
                    print("%d trajectories checked" % traj_idx)
        else:
            mananger = multiprocess.Manager()
            queue = mananger.Queue()
            jobs = []
            workload = math.floor(traj_num/args.process)
            for proc_idx in range(args.process):
                if proc_idx == args.process - 1:
                    participents_load = list(range(proc_idx*workload,traj_num))
                else:
                    participents_load = list(range(proc_idx*workload,(proc_idx+1)*workload))
                p = multiprocess.Process(target=ground_truth_worker,args=(dataset,proc_idx,candidates,participents_load,queue,args.verbose))
                jobs.append(p)
                p.start()

            for p in jobs:
                p.join()
            
            if args.verbose:
                print("Aggregating...")

            proc_results = [queue.get() for j in jobs]

            for proc_res in proc_results:
                for key,value in proc_res.items():
                    support_count[key] += value

            
        fragments = [key for key,value in support_count.items() if value >= k]
        for key,value in support_count.items():
            if value >= k:
                res[key] = value

        print("%d-fragments: %d admitted" % (frag_len,len(fragments)))






