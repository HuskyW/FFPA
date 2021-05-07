'''
    Calculate ground truth with standard Apriori algorithm
'''

from utils.Candidate import generateCandidates
from collections import defaultdict
from models.DataSet import DataSet,Trajectory
from utils.Naming import GroundTruthPickleName, SupportCountPickleName
import pickle
import multiprocess
import math
from utils.Print import printRound

def ground_truth_worker(dataset,process_idx,candidates,participents,queue,verbose):
    num_milestone = 5
    milestone = math.floor(len(participents)/num_milestone)
    local_support_count = defaultdict(lambda : 0)
    for idx in range(len(participents)):
        if idx > 0 and idx % milestone == 0 and verbose:
            print("Worker %2d: %d%% done" % (process_idx,int(round(idx*100/len(participents)))))
        client_idx = participents[idx]
        for candi in candidates:
            if dataset.checkSubSeq(client_idx,candi) is True:
                local_support_count[candi] += 1

    queue.put(local_support_count)
    if verbose:
        print("Worker %2d: all done" % process_idx)
    return

def groundTruth(dataset,args):
    k = int(args.k/args.duplicate)
    l = args.l
    traj_num = dataset.get_traj_num()
    
    # 1-fragments
    printRound(1)
    support_count = defaultdict(lambda : 0)
    for traj_idx in range(traj_num):
        locations = dataset.allLocations(traj_idx)
        for loc in locations:
            support_count[loc] += 1
    # filter out
    fragments_orig = [key for key,value in support_count.items() if value >= k]
    fragments = []
    for frag in fragments_orig:
        fragments.append([frag])
    if args.verbose:
        print("1-fragments generated")

    # longer fragments
    for frag_len in range(2,l+1):
        printRound(frag_len)
        candidates = generateCandidates(fragments)
        print("%d-fragments: %d candidates" % (frag_len,len(candidates)))
        if len(candidates) == 0:
            print('No candidate with length ' + frag_len)
            return None
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

            results = [queue.get() for j in jobs]

            for res in results:
                for key,value in res.items():
                    support_count[key] += value

            
        fragments = [key for key,value in support_count.items() if value >= k]

        print("%d-fragments: %d admitted" % (frag_len,len(fragments)))


    fragments = [key for key,value in support_count.items() if value >= k]
    pickleName = GroundTruthPickleName(args)
    with open(pickleName,'wb') as fp:
        pickle.dump(fragments,fp)
    results = [(key,value) for key,value in support_count.items() if value >= k]
    results = sorted(results,key=lambda item:item[1],reverse=True)
    for frag in results:
        print('%s: %d' % (str(frag[0]),frag[1]))

    support_count_record = {}
    support_count_record['data'] = results
    support_count_record['k'] = k
    scName = SupportCountPickleName(args)
    with open(scName,'wb') as fp:
        pickle.dump(support_count_record,fp)

    return fragments


def config_ground_truth_worker(dataset,process_idx,candidates,participents,weights,queue,verbose):
    num_milestone = 5
    milestone = math.floor(len(participents)/num_milestone)
    local_support_count = defaultdict(lambda : 0)
    for idx in range(len(participents)):
        if idx > 0 and idx % milestone == 0 and verbose:
            print("Worker %2d: %d%% done" % (process_idx,int(round(idx*100/len(participents)))))
        client_idx = participents[idx]
        traj = dataset.get_trajectory(client_idx)
        for candi in candidates:
            if traj.checkSubSeq(candi) is True:
                local_support_count[candi] += weights[client_idx]

    queue.put(local_support_count)
    if verbose:
        print("Worker %2d: all done" % process_idx)
    return

def groundTruthFromConfig(config,args):
    '''
        Used for generated dataset (zipf) where config is simpler to estimate
    '''
    metadata = config[1]
    record = config[0]
    n_loc = metadata['num_loc']
    dataset = DataSet(n_loc)

    support_count_weight = []

    for key, value in record.items():
        traj = Trajectory(key)
        dataset.add_trajectory(traj)
        support_count_weight.append(value)
    
    k = int(args.k / args.duplicate)
    l = args.l
    traj_num = dataset.get_traj_num()
    
    # 1-fragments
    support_count = defaultdict(lambda : 0)
    for traj_idx in range(traj_num):
        traj = dataset.get_trajectory(traj_idx)
        locations = traj.allLocations()
        for loc in locations:
            support_count[loc] += support_count_weight[traj_idx]
    # filter out
    fragments_orig = [key for key,value in support_count.items() if value >= k]
    fragments = []
    for frag in fragments_orig:
        fragments.append([frag])
    if args.verbose:
        print("1-fragments generated")

    # longer fragments
    for frag_len in range(2,l+1):
        candidates = generateCandidates(fragments)
        if args.verbose:
            print("%d-fragments: %d candidates" % (frag_len,len(candidates)))
        if len(candidates) == 0:
            print('No candidate with length ' + frag_len)
            return None
        support_count = defaultdict(lambda : 0)
        if args.process <= 0:
            for traj_idx in range(traj_num):
                traj = dataset.get_trajectory(traj_idx)
                for candi in candidates:
                    if traj.checkSubSeq(candi) is True:
                        support_count[candi] += support_count_weight[traj_idx]
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
                p = multiprocess.Process(target=config_ground_truth_worker,args=(dataset,proc_idx,candidates,participents_load,support_count_weight,queue,args.verbose))
                jobs.append(p)
                p.start()

            for p in jobs:
                p.join()
            
            if args.verbose:
                print("Aggregating...")

            results = [queue.get() for j in jobs]

            for res in results:
                for key,value in res.items():
                    support_count[key] += value


            if traj_idx % 10000 == 0 and args.verbose:
                print("%d trajectories checked" % traj_idx)
            
        fragments = [key for key,value in support_count.items() if value >= k]

        if args.verbose:
            print("%d-fragments: %d admitted" % (frag_len,len(fragments)))
    
    return fragments

