from models.Candidate import generateCandidates
from collections import defaultdict

def groundTruth(dataset,args):
    k = args.k
    l = args.l
    traj_num = dataset.get_traj_num()
    
    # 1-fragments
    support_counts = defaultdict(lambda : 0)
    for traj_idx in range(traj_num):
        traj = dataset.get_trajectory(traj_idx)
        locations = traj.allLocations()
        for loc in locations:
            support_counts[loc] += 1
    # filter out
    fragments_orig = [key for key,value in support_counts.items() if value >= k]
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
        support_counts = defaultdict(lambda : 0)
        for traj_idx in range(traj_num):
            traj = dataset.get_trajectory(traj_idx)
            for candi in candidates:
                if traj.checkSubSeq(candi) is True:
                    support_counts[candi] += 1

            if traj_idx % 10000 == 0 and args.verbose:
                print("%d trajectories checked" % traj_idx)
            
        fragments = [key for key,value in support_counts.items() if value >= k]

        if args.verbose:
            print("%d-fragments: %d admitted" % (frag_len,len(fragments)))
    
    return fragments