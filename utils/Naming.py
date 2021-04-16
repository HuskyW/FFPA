

def GroundTruthPickleName(args):
    name = "save/groundtruth_" + str(args.dataset) + '_l=' + str(args.l) + '_k=' + str(args.k) + '.pickle'
    return name