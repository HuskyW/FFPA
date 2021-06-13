import argparse

def args_parser():
    parser = argparse.ArgumentParser()
    # Basic params
    parser.add_argument('--k', type=int, default=50, help="param of k-anonymity")
    parser.add_argument('--xi', type=float, default=0.1, help="allowed error rate for k-anonymity")
    parser.add_argument('--epsilon', type=float, default=10.0, help="param of LDP")
    parser.add_argument('--num_participants', type=int, default=100000, help="number of participating clients")
    parser.add_argument('--mode', type=str, default='ffpa', help="mode: groundtruth || ffpa")
    parser.add_argument('--round_threshold', type=int, default=20, help="only work for triehh: maximum number of rounds")

    # Advanced params
    parser.add_argument('--num_candidate', type=int, default=10, help="maximum candidates assigned to one client")
    parser.add_argument('--softk', action='store_true', help='loosy k parameter thresholding')
    parser.add_argument('--admit_threshold', type=int, default=-1, help="Number of admit fragments in each round, -1: no thresholding")
    
    # Settings
    parser.add_argument('--dataset', type=str, default='msnbc', help="msnbc || zipf || oldenburg")
    parser.add_argument('--duplicate', type=int, default=1, help="virtually duplicate the dataset")
    parser.add_argument('--load_pickle', action='store_true', help='read dataset form pickle file')
    parser.add_argument('--write_pickle', action='store_true', help='store dataset into pickle file, do not work when --load_pickle is activated')

    parser.add_argument('--min_length', type=int, default=3, help="minimal length of each trajectory")
    parser.add_argument('--max_length', type=int, default=None, help="maximal length of each trajectory")
    parser.add_argument('--verbose', action='store_true', help='verbose print')

    parser.add_argument('--process', type=int, default=0, help="number of worker processes, 0: single process")

    # SFP params
    parser.add_argument('--sfp_threshold', type=int, default=10, help="number of popular 2-fragments at each location")
    parser.add_argument('--k_cut', type=float, default=1, help="cut down the value of k for better performance")

    args = parser.parse_args()
    return args