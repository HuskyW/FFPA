from copy import deepcopy

def linkFragment(a,b):
    if len(a) == 1:
        res = (a[0],b[0])
        return res
    
    frag_len = len(a)
    if a[1:frag_len] != b[0:frag_len-1]:
        return None
    res = list(deepcopy(a))
    res.append(b[frag_len-1])
    return tuple(res)

def generateCandidates(data):
    # Generate candidates with length l+1 based on fragments with length l
    # data is a list of fragments, while fragment is a list of location
    candidates = set()
    for i in data:
        for j in data:
            candi = linkFragment(i,j)
            if candi is not None:
                candidates.add(candi)
    return candidates
