# Setup

## Installation

### Install via pip:

`pip3 install https://github.com/Lonami/pyndustric/archive/refs/heads/master.zip`

or

`python3 -m pip install https://github.com/Lonami/pyndustric/archive/refs/heads/master.zip`

### Install from source

To install from the source code (for development or something)

    git clone <your git repo>
    cd <repo folder>
    python3 setup.py install

## Usage

### Compiling a program

`python3 -m pyndustric yourprogram.py`

The compiled program will be printed to standard output by default. You can also redirect the output to a file to create a new file with the compiled program:

`python3 -m pyndustric yourprogram.py > yourprogram.mlog`

If the optional dependency autoit is installed, -c or --clipboard can be used to automatically copy the code to the clipboard which allows for very fast edit cycles:

`python3 -m pyndustric -c yourprogram.py`

### Editor autocomplete

To get autocompletion and documentation in your editor (like vscode hovering/linting) add this to the beggining of the .py:

`from pyndustri import *`

Note: Some parts of the code will be warned (for example building variables like switch1 will show variable underfined warning)