# NASBench-PyTorch
NASBench-PyTorch is a PyTorch implementation of the search space
[NAS-Bench-101](https://github.com/google-research/nasbench) including the training of the networks[**](#note). The original
implementation is written in TensorFlow, and this projects contains
some files from the original repository (in the directory
`nasbench_pytorch/model/`).

**Important:** if you want to reproduce the original results, please refer to the
[Reproducibility](#repro) section.

# Overview
A PyTorch implementation of *training* of NAS-Bench-101 dataset: [NAS-Bench-101: Towards Reproducible Neural Architecture Search](https://arxiv.org/abs/1902.09635).
The dataset contains 423,624 unique neural networks exhaustively generated and evaluated from a fixed graph-based search space.

# Usage
You need to have PyTorch installed.

You can install the package by running `pip install nasbench_pytorch`. The second possibility is to install from source code:

1. Clone this repo
```
git clone https://github.com/romulus0914/NASBench-PyTorch
cd NASBench-PyTorch
```

2. Install the project
```
pip install -e .
```

The file `main.py` contains an example training of a network. To see
the different parameters, run:

```
python main.py --help
```

### Train a network by hash
To train a network whose architecture is queried from NAS-Bench-101
using its unique hash, install the original [nasbench](https://github.com/google-research/nasbench)
repository. Follow the instructions in the README, note that you
need to install TensorFlow. If you need TensorFlow 2.x, install
[this fork](https://github.com/gabrielasuchopar/nasbench) of the
repository instead.

Then, you can get the PyTorch architecture of a network like this:

```python
from nasbench_pytorch.model import Network as NBNetwork
from nasbench import api


nasbench_path = '$path_to_downloaded_nasbench'
nb = api.NASBench(nasbench_path)

net_hash = '$some_hash'  # you can get hashes using nasbench.hash_iterator()
m = nb.get_metrics_from_hash(net_hash)
ops = m[0]['module_operations']
adjacency = m[0]['module_adjacency']

net = NBNetwork((adjacency, ops))
```

Then, you can train it just like the example network in `main.py`.

# Architecture
Example architecture (picture from the original repository)
![archtecture](./assets/architecture.png)

# Reproducibility <a id="repro"></a>
The code should closely match the TensorFlow version (including the hyperparameters), but there are some differences:
- RMSProp implementation in TensorFlow and PyTorch is **different**
  - For more information refer to [here](https://github.com/pytorch/pytorch/issues/32545) and [here](https://github.com/pytorch/pytorch/issues/23796).
  - Optionally, you can install pytorch-image-models where a [TensorFlow-like RMSProp](https://github.com/rwightman/pytorch-image-models/blob/main/timm/optim/rmsprop_tf.py#L5) is implemented
    - `pip install timm`
  - Then, pass `--optimizer rmsprop_tf` to `main.py` to use it


- You can turn gradient clipping off by setting `--grad_clip_off True`


- The original training was on TPUs, this code enables only GPU and CPU training
- Input data augmentation methods are the same, but due to randomness they are not applied in the same manner
  - Cause: Batches and images cannot be shuffled as in the original TPU training, and the augmentation seed is also different
- Results may still differ due to TensorFlow/PyTorch implementation differences

Refer to this [issue](https://github.com/romulus0914/NASBench-PyTorch/issues/6) for more information and for comparison with API results.

# Disclaimer
Modified from [NASBench: A Neural Architecture Search Dataset and Benchmark](https://github.com/google-research/nasbench).
*graph_util.py* and *model_spec.py* are directly copied from the original repo. Original license can be found [here](https://github.com/google-research/nasbench/blob/master/LICENSE).

<a id="note"></a>
**Please note that this repo is only used to train one possible architecture in the search space, not to generate all possible graphs and train them.
