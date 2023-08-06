# hg38genome

[![Build Status](https://travis-ci.org/kylessmith/hg19_genome.svg?branch=master)](https://travis-ci.org/kylessmith/hg38genome) [![PyPI version](https://badge.fury.io/py/hg19_genome.svg)](https://badge.fury.io/py/hg38genome)
[![Coffee](https://img.shields.io/badge/-buy_me_a%C2%A0coffee-gray?logo=buy-me-a-coffee&color=ff69b4)](https://www.buymeacoffee.com/kylessmith)

A package to work with hg38 genomic intervals.


## Install

If you dont already have numpy and scipy installed, it is best to download
`Anaconda`, a python distribution that has them included.  
```
    https://continuum.io/downloads
```

Dependencies can be installed by:

```
    pip install -r requirements.txt
```

PyPI install, presuming you have all its requirements installed:
```
    pip install hg38genome(not yet!!)
```

## Usage

```python
# ailist version: 0.1.7
from hg38genome import Hg38Genome
genome = Hg38Genome()
genome.n_CpGs

genome.n_bases

genome.tss()

genome.tss(upstream=1000, downstream=1000)

```

