from models.Handlers import Handler
from utils.Sampling import sampleClients
from utils.Print import printRound
import multiprocess
from collections import defaultdict
import multiprocess

class Node():
    def __init__(self,parent,data,uid):
        self.data = data
        self.children = []
        self.id = uid
        self.parent = parent

    def getData(self):
        return self.data

    def getId(self):
        return self.id

    def checkChildren(self,data):
        for child in self.children:
            if child.getData() == data:
                return child
        return None

    def addChild(self,child):
        self.children.append(child)
        return

    


class Tree():
    def __init__(self):
        self.root = Node(None,None,0)
        self.node_list = [self.root]
        self.next_id = 1
    
    def addLeaf(self,parent_id,data):
        leaf = Node(parent_id,data,self.next_id)
        self.node_list.append(leaf)
        self.next_id += 1
        self.node_list[parent_id].addChild(leaf)

    def checkTrie(self,trie):
        current_node = self.root
        for idx in range(len(trie)):
            next_node = current_node.checkChildren(trie[idx])
            if next_node is None:
                return None
            current_node = next_node
        return current_node.getId()

    def traceBack(self,target_id):
        trace = []
        current_id = target_id
        while self.node_list[current_id].parent is not None:
            next_id = self.node_list[current_id].parent
            write_data = self.node_list[current_id].getData()
            if write_data is None:
                trace.reverse()
                return trace
            trace.append(write_data)
            current_id = next_id
        trace.reverse()
        return trace

    def allTrie(self):
        res = []
        for i in range(len(self.node_list)):
            if len(self.node_list[i].children) == 0: #leaf
                trace = self.traceBack(i)
                res.append(trace)
        return res


        


class TriehhHandler(Handler):
    def __init__(self,args,dataset):
        self.args = args
        self.dataset = dataset
        self.tree = Tree()
        self.orig_traj_num = self.dataset.get_traj_num()
        self.client_num = self.orig_traj_num * self.args.duplicate
        self.threshold = self.args.num_participants * self.args.k / self.client_num

    def clientVote(self,traj,curr_round):
        if len(traj) < curr_round:
            return None
        trie = traj[0:curr_round-1]
        prefix = self.tree.checkTrie(trie)
        if prefix is None:
            return None
        return (prefix,traj[curr_round-1])

    def fixTrieLength(self,tries):
        res = set()
        target_len = self.args.l
        for trie in tries:
            trie_len = len(trie)
            for i in range(0,trie_len-target_len+1):
                piece = tuple(trie[i:i+target_len])
                res.add(piece)
        return list(res)

    def __worker(self,proc_idx,curr_round,participents,queue):
        local_support_count = defaultdict(lambda : 0)
        for i in range(len(participents)):
            client_idx = participents[i]
            res = self.clientVote(self.dataset[client_idx],curr_round)
            if res is not None:
                local_support_count[res] += 1
        queue.put(local_support_count)
        if self.args.verbose:
            print("Worker %2d: all done" % proc_idx)
        return



    def run(self):
        for round_idx in range(1,self.args.round_threshold+1):
            printRound(round_idx)
            participents = sampleClients(self.args,self.orig_traj_num,self.args.num_participants)
            support_count = defaultdict(lambda : 0)
            if self.args.process <= 0:
                for idx in range(len(participents)):
                    client_idx = participents[idx]
                    if idx % 2000000 == 0 and idx > 0 and self.args.verbose:
                        print("%d trajectories checked" % idx)
                    vote = self.clientVote(self.dataset.get_trajectory(client_idx),round_idx)
                    if vote is not None:
                        support_count[vote] += 1
            else:
                mananger = multiprocess.Manager()
                queue = mananger.Queue()
                jobs = []
                workload = int(len(participents)/self.args.process)
                for proc_idx in range(self.args.process):
                    if proc_idx == self.args.process - 1:
                        participents_load = participents[proc_idx*workload:len(participents)]
                    else:
                        participents_load = participents[proc_idx*workload:(proc_idx+1)*workload]
                    p = multiprocess.Process(target=self.__worker,args=(proc_idx,round_idx,participents_load,queue))
                    jobs.append(p)
                    p.start()

                for p in jobs:
                    p.join()
                
                if self.args.verbose:
                    print("Aggregating...")

                results = [queue.get() for j in jobs]
                for res in results:
                    for key,value in res.items():
                        support_count[key] += value
            
            
            
            update = 0
            for key, value in support_count.items():
                if value >= self.threshold:
                    update += 1
                    self.tree.addLeaf(key[0],key[1])
            
            print("%d leaf added" % update)

            if update == 0:
                break
        
        tries = self.tree.allTrie()
        tries_fixed = self.fixTrieLength(tries)
        return tries_fixed
                
            

        


    
            

    


if __name__ == '__main__':
    data = ['a','p','p','l','e','s']
    t = Tree()
    t.addLeaf(0,'a')
    for i in range(1,6):
        target = t.checkTrie(data[0:i])
        if target is None:
            print("Not found")
            exit(0)
        t.addLeaf(target,data[i])
    final = t.checkTrie(data)
    print(t.traceBack(final))

