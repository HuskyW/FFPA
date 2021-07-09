from models.DataSet import Trajectory, SeqDataSet
import pickle


def loadMsnbc(minLength=3,maxLength=None):
    msnbc_path = 'data/msnbc/msnbc990928.seq'
    with open(msnbc_path) as fp:
        lines = fp.readlines()
        line_num = len(lines)
    dataset = SeqDataSet(list(range(17)))
    for i in range(7,line_num):
        line = lines[i]
        line_split = line.split()

        for i in range(len(line_split)):
            line_split[i] = int(line_split[i]) - 1 # locations starts form 0
        
        if minLength is not None and len(line_split) < minLength:
            continue

        if maxLength is not None and len(line_split) > maxLength:
            continue

        traj = Trajectory(line_split)
        dataset.add_line(traj)

    with open("./data/msnbc.pickle",'wb') as fp:
        pickle.dump(dataset,fp)
    
    return dataset

def loadMsnbc_trimmed(requiredlocations,minLength=3,maxLength=None):
    msnbc_path = 'data/msnbc/msnbc990928.seq'
    with open(msnbc_path) as fp:
        lines = fp.readlines()
        line_num = len(lines)
    dataset = SeqDataSet(list(range(requiredlocations)))

    location_count = {}
    for i in range(7,line_num):
        line = lines[i]
        line_split = line.split()

        for i in range(len(line_split)):
            line_split[i] = int(line_split[i]) # locations starts form 0
        
        if minLength is not None and len(line_split) < minLength:
            continue

        if maxLength is not None and len(line_split) > maxLength:
            continue

        for k in line_split:
            if k not in location_count.keys():
                location_count[k] = 0
            location_count[k] += 1
        
    locationsort = sorted(location_count.items(),key=lambda x: x[1],reverse=True)
    locationdict = {}
    for i in range(requiredlocations):
        locationdict[locationsort[i][0]] = i
    print(locationdict)

    for i in range(7,line_num):
        line = lines[i]
        line_split = line.split()

        for i in range(len(line_split)):
            line_split[i] = int(line_split[i]) # locations starts form 0
        
        if minLength is not None and len(line_split) < minLength:
            continue

        if maxLength is not None and len(line_split) > maxLength:
            continue

        trimmedtraj = []
        for k in line_split:
            if k not in locationdict.keys():
                continue
            trimmedtraj.append(locationdict[k])
        
        traj = Trajectory(trimmedtraj)
        dataset.add_line(traj)

    filepath = "./data/msnbc" + str(requiredlocations) + '.pickle'
    with open(filepath,'wb') as fp:
        pickle.dump(dataset,fp)
    
    return dataset


if __name__ == '__main__':
    #ds = loadMsnbc()
    loadMsnbc_trimmed(requiredlocations=14)
