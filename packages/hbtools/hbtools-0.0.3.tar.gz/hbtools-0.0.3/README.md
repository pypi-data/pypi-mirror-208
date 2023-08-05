# hbtools

[![PyPI](https://img.shields.io/pypi/v/hbtools?color=green&style=flat)](https://pypi.org/project/hbtools)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hbtools?style=flat)](https://pypi.org/project/hbtools)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/hbtools?style=flat-square)](https://pypistats.org/packages/hbtools)
[![License](https://img.shields.io/pypi/l/hbtools?style=flat)](https://opensource.org/licenses/MIT)
![Linting](https://github.com/hoel-bagard/hbtools/actions/workflows/pre-commit.yaml/badge.svg)
![Tests](https://github.com/hoel-bagard/coco-types/actions/workflows/nox.yaml/badge.svg)

Package containing a few python utils functions.

## Installation

The package is available on pypi [here](https://pypi.org/project/hbtools/) you can install it with:

```
pip install hbtools
```

## Usage

### Logger
```python
from hbtools import create_logger
logger = hbtools.create_logger("MyLogger", verbose_level="debug")
logger.debug("Debug message")
```

### Prints
```python
from hbtools import clean_print
clean_print("Processing sample (1/10)", end = "\r")
clean_print("Processing sample (10/10)", end = "\n")

from hbtools import yes_no_prompt
yes_no_prompt("Would you like to continue ?")
```

### Image
```python
import numpy as np
from hbtools import show_img
img = np.zeros((200, 200, 3))
show_img(img)
```

Additionally, if using a server through ssh, you can install this package with extras for displaying images to the terminal:
```
pip install hbtools[terminal]
```
