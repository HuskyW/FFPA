from models.DataSet import Trajectory, DataSet
import pickle


def loadMsnbc(minLength=None,maxLength=None,dump=True):
    msnbc_path = 'data/msnbc/msnbc990928.seq'
    with open(msnbc_path) as fp:
        lines = fp.readlines()
        line_num = len(lines)
    dataset = DataSet(17)
    for i in range(7,line_num):
        line = lines[i]
        line_split = line.split()
        line_split = list(map(int, line_split))

        for i in range(len(line_split)):
            line_split[i] -= 1 # locations starts form 0
        
        if minLength is not None and len(line_split) < minLength:
            continue

        if maxLength is not None and len(line_split) > maxLength:
            continue

        #traj = Trajectory(line_split)
        dataset.add_trajectory(line_split)

    if dump is True:
        with open('data/msnbc.pickle', 'wb') as fp:
            pickle.dump(dataset,fp)
    
    return dataset