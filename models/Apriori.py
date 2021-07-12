from models.DataSet import Trajectory
from copy import deepcopy


class seqUtils():
    def __init__(self):
        return

    def linker(self,a,b):
        if self.length(a) != self.length(b):
            return []
        l = self.length(a)
        if l == 1:
            data = [a[0],b[0]]
            traj = tuple(data)
            return [traj]
        
        a_piece = a[1:l]
        b_piece = b[0:l-1]

        comp = (a_piece == b_piece)
        if comp is False:
            return []

        data = deepcopy(list(a))
        data.append(b[l-1])
        traj = tuple(data)
        return [traj]

    def sub(self,target):
        l = self.length(target)
        if l == 1:
            return []
        target_list = list(target)
        sub1 = target_list[0:l-1]
        sub2 = target_list[1:l]
        return [tuple(sub1),tuple(sub2)]

    def length(self,target):
        return len(target)


    
class itemUtils():
    def __init__(self):
        return

    def linker(self,a,b):
        if a == b:
            return []
        if self.length(a) != self.length(b):
            return []
        l = self.length(a)
        if l == 1:
            data = [a[0],b[0]]
            data.sort()
            traj = tuple(data)
            return [traj]
        
        a_piece = a[0:l-1]
        b_piece = b[0:l-1]

        comp = (a_piece == b_piece)
        if comp is False:
            return []

        data = deepcopy(list(a))
        data.append(b[l-1])
        data.sort()
        traj = tuple(data)
        return [traj]

    def sub(self,target):
        l = self.length(target)
        if l == 1:
            return []
        target_list = list(target)
        res = []
        for i in target_list:
            temp = deepcopy(target_list)
            temp.remove(i)
            temp.sort()
            res.append(tuple(temp))

        return res

    def length(self,target):
        return len(target)

class hitterUtils():
    def __init__(self):
        return

    def linker(self,a,b):
        return []

    def sub(self,target):
        return []

    def length(self,target):
        return 1
