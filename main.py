from LoadData import loadMsnbc
from utils.Options import args_parser
import pickle
from models.GroundTruth import groundTruth, groundTruthFromConfig
from Handlers import FastPubHandler
from utils.Naming import GroundTruthPickleName


def ckeckWithGroundTruth(result,truth):
    tp = 0
    for frag in result:
        if frag in truth:
            tp += 1
    precision = tp/len(result)
    recall = tp/len(truth)
    print("Precision: %.2f; Recall: %.2f" % (precision,recall))
    return


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
    else:
        print("Bad argument: dataset")


    if args.mode == 'groundtruth':
        if args.dataset == 'zipf':
            fragments = groundTruthFromConfig(config,args)
            print(fragments)
        else:
            fragments = groundTruth(dataset,args)
            print(fragments)
    elif args.mode == 'fastpub':
        handler = FastPubHandler(args,dataset)
        fragments = handler.run()
        for frag in fragments:
            print(frag)


    if args.dataset == 'zipf':
        ground_truth = groundTruthFromConfig(config,args)
    elif args.dataset == 'msnbc':
        pickleName = GroundTruthPickleName(args)
        with open(pickleName,'rb') as fp:
            ground_truth = pickle.load(fp)
    ckeckWithGroundTruth(fragments,ground_truth)

