import numpy as np
from copy import deepcopy
import random

def sampleClients(args,orig_traj_num):
    m = args.num_participants
    clients = []
    for i in range(args.duplicate):
        clients.extend(list(range(orig_traj_num)))
    if m <= len(clients):
        res = np.random.choice(clients,m,replace=False)
    else:
        res = np.random.choice(clients,m,replace=True)
    return res