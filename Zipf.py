import pickle
from models.DataSet import DataSet, Trajectory
import numpy as np


def randomTraj(l,n_loc):
    res = []
    for i in range(l):
        res.append(np.random.randint(n_loc))
    return tuple(res)

def generateZipf(n_traj=1000000,n_loc=20,n_traj_options=5000,l=10):
    dataset = DataSet(n_loc)

    # generate candidates of possible traj
    candidates = set()
    while len(candidates) < n_traj_options:
        traj = randomTraj(l,n_loc)
        candidates.add(traj)
    candidates = list(candidates)

    print("Candidates generated")

    # zipf distribution
    weights_raw = [1/i for i in range(1,n_traj_options+1)]
    weights_norm = [float(i)/sum(weights_raw) for i in weights_raw]

    record = {}

    for i in range(n_traj):
        if i % 10000 == 0 and i > 0:
            print("%d records generated" % i)
        selected_idx = np.random.choice(n_traj_options,p=weights_norm)
        selected_list = candidates[selected_idx]
        #selected_traj = Trajectory(selected_list)
        dataset.add_trajectory(selected_list)

        selected_conf = tuple(selected_list)
        if selected_conf not in record.keys():
            record[selected_conf] = 0
        record[selected_conf] += 1

    print("Dataset generated")

    metadata = {'num_loc':n_loc}
    config = [record,metadata]

    return dataset, config
    


if __name__ == '__main__':
    dataset,config = generateZipf()
    with open('data/zipf.pickle', 'wb') as fp:
        pickle.dump(dataset,fp)
    with open('data/zipf_config.pickle', 'wb') as fp:
        pickle.dump(config,fp)