import numpy as np

def randomBits(data,eta):
    # randomize a list of bits
    for i in range(len(data)):
        draw = np.random.random_sample()
        if draw < eta:
            data[i] = 1 - data[i]
    return data

def randomInt(data,eta,loc_num):
    draw = np.random.random_sample()
    if draw < eta:
        locs = set(range(loc_num))
        locs.remove(data)
        return np.random.choice(list(locs))
    return data
