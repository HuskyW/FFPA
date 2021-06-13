import numpy as np

class Randomizer():
    def __init__(self,args):
        self.args = args
        self.eta = self.args.eta
    
    def randomBits(self,data):
        # randomize a list of bits
        for i in range(len(data)):
            draw = np.random.random_sample()
            if draw < self.eta:
                data[i] = 1 - data[i]
        return data


