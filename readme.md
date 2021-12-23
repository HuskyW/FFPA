# FedFPM: A Unified Federated Analytics Framework for Collaborative Frequent Pattern Mining

Note that FedFPM is named FFPA in this implementation.

## Introduction
FedFPM is a unified federated analytics framework for frequent pattern mining on distributed data. It satisfies local differential privacy as a strong local privacy preservation scheme. It gains high data utility (F1 score) of obtained data over benchmarks with lower client usage. This implementation allows FedFPM to work on frequent item mining (FIM), frequent itemset mining (FIsM), and frequent sequence mining (FSM), where FedFPM still has the potential to work on other scenarios. 

## Features
- functionality of FedFPM on a simulated environment
- three datasets: Kosarak for FIM, MovieLens for FIsM, and MovieLens for FSM
- two benchmarks: basic RAPPOR (with one-hot encoding) for FIM and FIsM, and SFP for FSM
- find the groundtruth frequent patterns with the Apriori algorithm
- multiprocessing in simulation (quite helpful for SFP)

## Installation
```
python==3.8
numpy==1.20.1
multiprocess==0.70.11.1
```

## Preparation of datasets and groundtruths

The groundtruth of frequent patterns is required to calculate the F1 score. We place the datasets and groundtruth of frequent patterns in .... You can download the folders "./data" and "./groundtruth" and place them in the project root directory.

### You can also prepare those by yourself

To prepare the datasets, you can write datastructures like those in "./models/DataSet.py". Note that you should implement two structures: one is the local data in one client (like **class Trajectory**). The other is the global dataset of all clients (like **class SeqDataSet**). All the methods present in "./models/DataSet.py" should be implemented. After that, you need to pickle the latter structure and read them in "./main.py"

To prepare the groundtruths, you can run the codes with --mode==groundtruth, and the ground truth patterns will be automatically saved. Note that the save includes all patterns that exceed the frequency threshold (--k) along with their corresponding frequency. The save can work for all future runs with higher frequency, e.g., if you have run the code with "--mode==groundtruth --dataset=msnbc --k=0.01", you can simply run "--mode==ffpa --dataset=msnbc --k=0.02" and calculate the F1 score properly.

## Run the code

We present some lines to reproduce some of our experiment results.

Run FedFPM on MSNBC dataset (FSM), with target frequency 0.02

```
python main.py --dataset=msnbc --verbose --mode=ffpa --k=0.02  --process=14 --xi=0.01 --num_candidate=1 --num_participants=100000 --epsilon=2 --max_support=100000
```

Run SFP on MSNBC dataset (FSM), with target frequency 0.02

```
python main.py --dataset=msnbc --verbose --mode=sfp --k=0.02  --process=14 --num_participants=26000000 --epsilon=2
```

Run FedFPM on Kosarak dataset (FIM), with target frequency 0.02
```
python main.py --dataset=kosarak --verbose --mode=ffpa --k=0.02  --process=14 --xi=0.01 --num_candidate=1 --num_participants=1000000 --epsilon=2 --max_support=100000
```

Run RAPPOR on Kosarak dataset (FIM), with target frequency 0.02
```
python main.py --dataset=kosarak --verbose --mode=rappor --k=0.02  --process=14 --num_participants=17000000 --epsilon=2
```

## Citation format

Z. Wang, Y. Zhu, D. Wang, and Z. Han, "FedFPM: A Unified Federated Analytics Framework for Collaborative Frequent Pattern Mining," In *Proceeding of IEEE International Conference on Computer Communications (INFOCOM)*, 2022.

```
@inproceedings{wang2022fedfpm,
  title={FedFPM: A Unified Federated Analytics Framework for Collaborative Frequent Pattern Mining},
  author={Wang, Zibo and Zhu, Yifei and Wang, Dan and Han, Zhu},
  booktitle={Proceeding of IEEE International Conference on Computer Communications (INFOCOM)},
  year={2022}
}
```