

def SupportCountPickleName(args):
    k = int(args.k/args.duplicate)
    name = "save/supportcount_" + str(args.dataset) + '.pickle'
    return name