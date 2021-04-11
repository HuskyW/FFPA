from LoadData import loadMsnbc
from models.DataSet import DataSet, Trajectory
from utils.Options import args_parser


if __name__ == '__main__':
    args = args_parser()
    dataset = loadMsnbc(dump=False,minLength=5)
    traj = dataset.get_trajectory(79)
    print(traj.uploadOne())