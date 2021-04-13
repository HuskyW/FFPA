from LoadData import loadMsnbc
from models.DataSet import DataSet, Trajectory
from utils.Options import args_parser
import pickle


if __name__ == '__main__':
    args = args_parser()
    if args.load_pickle is True:
        with open('data/msnbc.pickle') as fp:
            dataset = pickle.load(fp)
    else:
        dataset = loadMsnbc(dump=args.write_pickle,minLength=args.min_length,maxLength=args.max_length)
    traj = dataset.get_trajectory(79)
    print(traj.uploadOne())