import os
import pickle
from sys import exit
 

from utils.Options import args_parser
from models.GroundTruth import groundTruth
from models.Handlers import FfpaHandler
from models.Rappor import RapporHandler
from models.Sfp import SfpHandler
from utils.Naming import SupportCountPickleName
from utils.Print import printLog


def ckeckWithGroundTruth(result,truth):
    tp = 0
    for frag in result:
        if frag in truth:
            tp += 1
    precision = tp/len(result)
    recall = tp/len(truth)
    print("Precision: %.2f; Recall: %.2f" % (precision,recall))
    return precision, recall

def getGroundTruth(args):
    scName = SupportCountPickleName(args)
    if os.path.isfile(scName):
        with open(scName,'rb') as fp:
            sc_rec = pickle.load(fp)
            if sc_rec['k'] > (args.k/args.duplicate):
                print("Support count record invalid")
                exit(0)
            data = sc_rec['data']
            ground_truth = [i[0] for i in data.items() if i[1] >= (args.k/args.duplicate)]
            return ground_truth
    print("Ground truth not generated yet")
    exit(0)


if __name__ == '__main__':
    args = args_parser()
    if args.dataset == 'msnbc':
        args.pattern_type = 'sequence'
        with open('data/msnbc.pickle','rb') as fp:
            dataset = pickle.load(fp)
    elif args.dataset == 'movielens':
        args.pattern_type = 'itemset'
        with open('data/movielens.pickle','rb') as fp:
            dataset = pickle.load(fp)
    else:
        print("Bad argument: dataset")

    args.orig_k = args.k
    if args.k > 1:
        args.k = int(args.k)
    else:
        args.k = int(args.k * args.duplicate * dataset.get_line_num())

    if args.mode == 'groundtruth':
        if args.dataset == 'zipf':
            fragments = groundTruthFromConfig(config,args)
            print(fragments)
        else:
            res = groundTruth(dataset,args)
            print('%d subsequence found' % len(res))
            for key, value in res.items():
                print('%s: %d'%(str(key),value))
            support_count_record = {}
            support_count_record['data'] = res
            support_count_record['k'] = args.k
            scName = SupportCountPickleName(args)
            with open(scName,'wb') as fp:
                pickle.dump(support_count_record,fp)
        exit(0)

    if args.mode == 'ffpa':
        handler = FfpaHandler(args,dataset)
    elif args.mode == 'rappor':
        handler = RapporHandler(args,dataset)
    elif args.mode == 'sfp':
        handler = SfpHandler(args,dataset)
    fragments = handler.run()
    if args.verbose:
        print(fragments)

    if args.dataset == 'msnbc' or args.dataset == 'movielens':
        ground_truth = getGroundTruth(args)
    if len(fragments) > 0:
        precision, recall = ckeckWithGroundTruth(fragments,ground_truth)
    else:
        print("No fragment published")
        precision = -1.0
        recall = 0.0

    log = printLog(args,(precision,recall))
    with open('./save/log','a') as fp:
        fp.write(log)
