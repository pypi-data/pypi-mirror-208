<img src="./MEGABYTE.png" width="450px"></img>

## MEGABYTE-pytorch

Implementation of <a href="https://arxiv.org/abs/2305.07185">MEGABYTE</a>, Predicting Million-byte Sequences with Multiscale Transformers, in Pytorch

## Install

```bash
$ pip install MEGABYTE-pytorch
```

## Usage

```python
import torch
from MEGABYTE_pytorch import MEGABYTE

model = MEGABYTE(
    num_tokens = 16000,             # number of tokens, in the paper they had a codebook size of 16k
    dim = 512,                      # transformer model dimension
    max_seq_len = (1024, 4),        # sequence length for global and then local
    depth = (6, 4),                 # number of layers for global and then local
    dim_head = 64,                  # dimension per head
    heads = 8,                      # number of attention heads
)

x = torch.randint(0, 16000, (1, 1024, 4))

loss = model(x, return_loss = True)
loss.backward()

# then after much training

logits = model(x)

# and sample from the logits accordingly
# or you can use the generate function

sampled = model.generate(temperature = 0.9, filter_thres = 0.9) # (1, 1024, 4)
```

## Citations

```bibtex
@misc{yu2023megabyte,
    title   = {MEGABYTE: Predicting Million-byte Sequences with Multiscale Transformers}, 
    author  = {Lili Yu and Dániel Simig and Colin Flaherty and Armen Aghajanyan and Luke Zettlemoyer and Mike Lewis},
    year    = {2023},
    eprint  = {2305.07185},
    archivePrefix = {arXiv},
    primaryClass = {cs.LG}
}
```
