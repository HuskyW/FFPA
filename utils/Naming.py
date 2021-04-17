

def GroundTruthPickleName(args):
    k = int(args.k/args.duplicate)
    name = "save/groundtruth_" + str(args.dataset) + '_l=' + str(args.l) + '_k=' + str(k) + '.pickle'
    return name