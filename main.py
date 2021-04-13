from LoadData import loadMsnbc
from utils.Options import args_parser
import pickle
from models.GroundTruth import groundTruth


if __name__ == '__main__':
    args = args_parser()
    if args.load_pickle is True:
        with open('data/msnbc.pickle') as fp:
            dataset = pickle.load(fp)
    else:
        dataset = loadMsnbc(dump=args.write_pickle,minLength=args.min_length,maxLength=args.max_length)
    fragments = groundTruth(dataset,args)
    print(fragments)