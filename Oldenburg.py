from models.DataSet import DataSet, Trajectory
import math
import pickle


x_gridnum = 8
y_gridnum = 8

x_min = 0
y_min = 3000
x_max = 25000
y_max = 32000

x_space = (x_max-x_min)/x_gridnum
y_space = (y_max-y_min)/y_gridnum

def grid2loc(x,y):
    x_loc = math.floor((x-x_min)/x_space)
    y_loc = math.floor((y-y_min)/y_space)
    x_loc = max(x_loc,0)
    x_loc = min(x_loc,x_gridnum-1)
    y_loc = max(y_loc,0)
    y_loc = min(y_loc,y_gridnum-1)
    return x_loc * x_gridnum + y_loc

class OldenburgLoader():
    def __init__(self):
        self.dataset = DataSet(x_gridnum*y_gridnum)

    def save(self,path):
        with open(path, 'wb') as fp:
            pickle.dump(self.dataset,fp)

    def readFile(self,path):
        record = {}
        with open(path) as fp:
            lines = fp.readlines()
        for line in lines:
            line_split = line.split()
            traj_idx = int(line_split[1])
            x = int(round(float(line_split[5])))
            y = int(round(float(line_split[6])))
            if x < 0 or x > 40000 or y < 0 or y > 40000:
                continue
            pos = grid2loc(x,y)
            if traj_idx not in record.keys():
                record[traj_idx] = [pos]
            else:
                record[traj_idx].append(pos)
        for key, value in record.items():
            #traj = Trajectory(value)
            self.dataset.add_trajectory(value)
        

if __name__ == '__main__':
    filepathes = []
    for i in range(20):
        path = './data/oldenburg/1mfast_' + str(i) + '.dat'
        filepathes.append(path)
    loader = OldenburgLoader()
    for ipath in filepathes:
        loader.readFile(ipath)
        print('%s loaded' % ipath)
    loader.save('./data/oldenburg.pickle')
    print('Dataset created')