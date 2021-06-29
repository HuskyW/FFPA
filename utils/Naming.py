

def SupportCountPickleName(args):
    k = int(args.k/args.duplicate)
    name = "groundtruth/supportcount_" + str(args.dataset) + '.pickle'
    return name

def CandidateDriftName(args):
    name = "save/candidatedrift"
    return name

def LeaveNumPickleName(args):
    name = "save/leavelog.pickle"
    return name