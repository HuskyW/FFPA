import argparse

def args_parser():
    parser = argparse.ArgumentParser()
    # Basic params
    parser.add_argument('--k', type=float, default=10000, help="frequency threshold, when smaller than 1, it will be the proportion")
    parser.add_argument('--xi', type=float, default=0.1, help="allowed error rate for frequency estimation")
    parser.add_argument('--epsilon', type=float, default=10.0, help="param of LDP")
    parser.add_argument('--num_participants', type=int, default=100000, help="number of participating clients")
    parser.add_argument('--mode', type=str, default='ffpa', help="mode: groundtruth || ffpa || rappor")
    parser.add_argument('--num_candidate', type=int, default=1, help="candidates sent to each client")
    parser.add_argument('--max_support', type=int, default=-1, help="force candidates to leave the pool after its support exceeds the threshold")
    
    # Settings
    parser.add_argument('--dataset', type=str, default='msnbc', help="msnbc || movielens || ml12 || ml14 || ml16 || ml18 || ml20 || msnbc10 || msnbc14")
    parser.add_argument('--duplicate', type=int, default=1, help="virtually duplicate the dataset")
    parser.add_argument('--verbose', action='store_true', help='verbose print')
    parser.add_argument('--process', type=int, default=0, help="number of worker processes, 0: single process")
    parser.add_argument('--log_detail', action='store_true', help='log candidate details')


    # SFP settings
    parser.add_argument('--sfp_threshold', type=int, default=80, help="number of fragment puzzle held")

    args = parser.parse_args()
    return args