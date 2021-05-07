

def GroundTruthPickleName(args):
    k = int(args.k/args.duplicate)
    name = "save/groundtruth_" + str(args.dataset) + '_l=' + str(args.l) + '_k=' + str(k) + '.pickle'
    return name

def SupportCountPickleName(args):
    k = int(args.k/args.duplicate)
    name = "save/supportcount_" + str(args.dataset) + '_l=' + str(args.l) + '.pickle'
    return name