import time

def printRound(i):
    print('==================================')
    print('             Round %d             ' % i)
    print('==================================')

def printLog(args,performance):
    timestemp = str(time.strftime('%Y.%m.%d-%H:%M:%S',time.localtime(time.time())))
    record = timestemp + ';'
    record += '%s;' % str(args.dataset)
    record += '%s;' % str(args.mode)
    record += 'precision=%.4f;' % performance[0]
    record += 'recall=%.4f;' % performance[1]
    if args.mode == 'ffpa':
        record += 'round=%i;' % args.round
    record += 'dup=%d;' % args.duplicate
    record += 'm=%d;' % args.num_participants
    record += 'epsilon=%.1f;' % args.epsilon

    if args.orig_k > 1:
        record += 'k=%d;' % args.k
    else:
        record += 'k=%.2f;' % args.orig_k


    if args.mode == 'ffpa':
        record += 'xi=%f;' % args.xi
        record += 'c=%d;' % args.num_candidate
        record += 'max_support=%d;' % args.max_support
    
    record += '\n'
    return record

def printLines(orig_list):
    res = ''
    for i in range(len(orig_list)):
        res += str(orig_list[i])
        if i < len(orig_list) - 1:
            res += '\n'
    return res