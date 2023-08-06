[![PyPI version](https://badge.fury.io/py/torch-hrp.svg)](https://badge.fury.io/py/torch-hrp)
[![PyPi downloads](https://img.shields.io/pypi/dm/torch-hrp)](https://img.shields.io/pypi/dm/torch-hrp)


# torch-hrp
Hashed Random Projection layer for PyTorch.

## Usage
<a href="https://github.com/satzbeleg/torch-hrp/blob/main/demo/Hashed%20Random%20Projections.ipynb">Hashed Random Projections (HRP), binary representations, encoding/decoding for storage</a> (notebook)


### Generate a HRP layer with a new hyperplane
The random projection or hyperplane is randomly initialized.
The initial state of the PRNG (`random_state`) is required (Default: 42) to ensure reproducibility.

```py
import torch_hrp as thrp
import torch

BATCH_SIZE = 32
NUM_FEATURES = 64
OUTPUT_SIZE = 1024

# demo inputs
inputs = torch.randn(size=(BATCH_SIZE, NUM_FEATURES))

# instantiate layer 
layer = thrp.HashedRandomProjection(
    output_size=OUTPUT_SIZE,
    input_size=NUM_FEATURES,
    random_state=42   # Default: 42
)

# run it
outputs = layer(inputs)
assert outputs.shape == (BATCH_SIZE, OUTPUT_SIZE)
```


### Instiantiate HRP layer with given hyperplane

```py
import torch_hrp as thrp
import torch

BATCH_SIZE = 32
NUM_FEATURES = 64
OUTPUT_SIZE = 1024

# demo inputs
inputs = torch.randn(size=(BATCH_SIZE, NUM_FEATURES))

# use an existing hyperplane
myhyperplane = torch.randn(size=(NUM_FEATURES, OUTPUT_SIZE))

# init layer
layer = thrp.HashedRandomProjection(hyperplane=myhyperplane)

# run it
outputs = layer(inputs)
```


### Multiprocessing on GPU-Server
The `HashedRandomProjection` layer has methods for multiprocessing of large numbers of examples for inference purposes (i.e. millions). These methods were adopted from the [SentenceTransformer code](https://github.com/UKPLab/sentence-transformers/blob/d928410803bb90f555926d145ee7ad3bd1373a83/sentence_transformers/SentenceTransformer.py#L206).
With the following script can be used to figure out how many example fit into the the RAM (e.g. 20 Mio.), 
and how big the chunk of example for each process can be to fit into the GPU memory (e.g. 4.5 Mio.)


```py
import torch
import torch_hrp as thrp

model_hrp = thrp.HashedRandomProjection(
    output_size=1024,
    input_size=768,  # the output dimension of the upstream embedding/transformer model
    random_state=42
)

# Requirements: 2x GPUs w 80 Gb; approx 200 Gb RAM
if __name__ == '__main__':  # multiprocessing spawning requires main
    x = torch.rand(int(20e6), 768)  # 20 Mio examples
    pool = model_hrp.start_pool()
    hashed = model_hrp.infer(x, pool, chunk_size=int(45e5))  # chunks of 4.5 Mio examples
    model_hrp.stop_pool(pool)
    torch.cuda.empty_cache()
```

see <a href="https://github.com/satzbeleg/torch-hrp/blob/main/demo/multiprocessing-on-gpu-server.py">demo/multiprocessing-on-gpu-server.py</a>

## Appendix

### Installation
The `torch-hrp` [git repo](http://github.com/satzbeleg/torch-hrp) is available as [PyPi package](https://pypi.org/project/torch-hrp)

```sh
pip install torch-hrp
pip install git+ssh://git@github.com/satzbeleg/torch-hrp.git
```

### Install a virtual environment (CPU)

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
pip install -r requirements-dev.txt --no-cache-dir
pip install -r requirements-demo.txt --no-cache-dir
```

(If your git repo is stored in a folder with whitespaces, then don't use the subfolder `.venv`. Use an absolute path without whitespaces.)


### Install with conda (GPU)

```sh
conda install -y pip
conda create -y --name gpu-venv-torch-hrp-dev python=3.9 pip
conda activate gpu-venv-torch-hrp-dev

conda install -y cudatoolkit=11.3.1 cudnn=8.3.2 -c conda-forge
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/
pip install torch==1.12.1+cu113 torchvision torchaudio -f https://download.pytorch.org/whl/torch_stable.html

# install other packages
pip install -e .
# pip install -r requirements.txt --no-cache-dir
pip install -r requirements-dev.txt --no-cache-dir
pip install -r requirements-demo.txt --no-cache-dir
```

### Python commands

* Jupyter for the examples: `jupyter lab`
* Check syntax: `flake8 --ignore=F401 --exclude=$(grep -v '^#' .gitignore | xargs | sed -e 's/ /,/g')`
* Run Unit Tests: `PYTHONPATH=. pytest`

Publish

```sh
# pandoc README.md --from markdown --to rst -s -o README.rst
python setup.py sdist 
twine upload -r pypi dist/*
```

### Clean up 

```sh
find . -type f -name "*.pyc" | xargs rm
find . -type d -name "__pycache__" | xargs rm -r
rm -r .pytest_cache
rm -r .venv
```


### Support
Please [open an issue](https://github.com/satzbeleg/torch-hrp/issues/new) for support.


### Contributing
Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/satzbeleg/torch-hrp/compare/).

### Acknowledgements
The "Evidence" project was funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) - [433249742](https://gepris.dfg.de/gepris/projekt/433249742) (GU 798/27-1; GE 1119/11-1).

### Citation
Please cite the arXiv Preprint when using this software for any purpose.

```
@misc{hamster2023rediscovering,
      title={Rediscovering Hashed Random Projections for Efficient Quantization of Contextualized Sentence Embeddings}, 
      author={Ulf A. Hamster and Ji-Ung Lee and Alexander Geyken and Iryna Gurevych},
      year={2023},
      eprint={2304.02481},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```
