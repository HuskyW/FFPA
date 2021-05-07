from LoadData import loadMsnbc
from utils.Options import args_parser
import pickle
from models.GroundTruth import groundTruth, groundTruthFromConfig
from models.Handlers import FastPubHandler
from models.Triehh import TriehhHandler
from utils.Naming import GroundTruthPickleName, SupportCountPickleName
from models.SFP import SfpHandler
from utils.Print import printLog
import os


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
    pickleName = GroundTruthPickleName(args)
    scName = SupportCountPickleName(args)
    if os.path.isfile(pickleName):
        with open(pickleName,'rb') as fp:
            ground_truth = pickle.load(fp)
        return ground_truth
    elif os.path.isfile(scName):
        with open(scName,'rb') as fp:
            sc_rec = pickle.load(fp)
            if sc_rec['k'] > (args.k/args.duplicate):
                print("Support count record invalid")
                exit(0)
            data = sc_rec['data']
            ground_truth = [i[0] for i in data if i[1] >= (args.k/args.duplicate)]
            return ground_truth
    print("Ground truth not generated yet")
    exit(0)


if __name__ == '__main__':
    args = args_parser()
    if args.dataset == 'msnbc':
        if args.load_pickle is True:
            with open('data/msnbc.pickle','rb') as fp:
                dataset = pickle.load(fp)
        else:
            dataset = loadMsnbc(dump=args.write_pickle,minLength=args.min_length,maxLength=args.max_length)
    elif args.dataset == 'zipf':
        with open('data/zipf.pickle','rb') as fp:
            dataset = pickle.load(fp)
        with open('data/zipf_config.pickle','rb') as fp:
            config = pickle.load(fp)
    elif args.dataset == 'oldenburg':
        with open('data/oldenburg.pickle','rb') as fp:
            dataset = pickle.load(fp)
    else:
        print("Bad argument: dataset")

    #dataset = [[1,4,7,8,3,5]]

    if args.mode == 'groundtruth':
        if args.dataset == 'zipf':
            fragments = groundTruthFromConfig(config,args)
            print(fragments)
        else:
            fragments = groundTruth(dataset,args)
            print(fragments)
    else:  
        if args.mode == 'fastpub':
            handler = FastPubHandler(args,dataset)
        elif args.mode == 'triehh':
            handler = TriehhHandler(args,dataset)
        elif args.mode == 'sfp':
            handler = SfpHandler(args,dataset)
        fragments = handler.run()
        if args.verbose:
            for frag in fragments:
                print(frag)


    if args.dataset == 'zipf':
        ground_truth = groundTruthFromConfig(config,args)
    elif args.dataset == 'msnbc' or args.dataset == 'oldenburg':
        ground_truth = getGroundTruth(args)
    if len(fragments) > 0:
        precision, recall = ckeckWithGroundTruth(fragments,ground_truth)
    else:
        print("No fragment published")
        precision = -1.0
        recall = 0.0

    if args.mode != 'groundtruth':
        log = printLog(args,(precision,recall))
        with open('./save/log','a') as fp:
            fp.write(log)


