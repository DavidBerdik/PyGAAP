# ![PyGAAP](res/logo.png)
# Python Graphical Authorship Attribution Program
The Python Graphical Authorship Attribution Program (PyGAAP) is an experimental reimplementation of the [Duquesne University Evaluating Variations in Language Lab's JGAAP](https://github.com/evllabs/JGAAP). Currently, PyGAAP is in its prototype phase and is by no means feature-complete. Although participation in the development of PyGAAP is encouraged, it should not be used for any serious text analysis at this time.


## Features
PyGAAP currently contains only a small subset of features from JGAAP and most features are not implemented. Several major missing features include:
* PyGAAP's GUI is not yet feature-complete
* PyGAAP does not yet support multi-threading
* PyGAAP does not yet provide extensive logging
* PyGAAP does not yet support feature set culling

## How to Contribute
To contribute to PyGAAP, simply fork the repository, create a new branch, make your desired changes, and submit a pull request. While adding a new module, you may find the [developer manual](/Developer_Manual.md) useful. Additionally, please consider opening an issue on this repository with an explanation of your planned contribution so that we may track who is working on what.

## How to Use
1. Clone the PyGAAP Git repository.
2. Install Python 3. Depending on your Operating System, it may already be installed.
3. Install the Python libraries required by PyGAAP. If you use pip, you can easily install the required libraries by executing one of the following commands from the root PyGAAP directory:
    1. `pip install -r requirements.txt`
    2. `python -m pip install -r requirements.txt`
	3. `pip3 install -r requirements.txt`
4. Run `python PyGAAP.py` to launch the PyGAAP GUI. Alternatively, PyGAAP can be executed on command line as well. Run `python PyGAAP.py -h` to print the command line help.

## Support
If you are having issues with PyGAAP that require support, please open an issue on this repository. As a reminder, PyGAAP is in early stages of development and should not be used for serious text analysis. If you require stable text analysis software, please use [JGAAP](https://github.com/evllabs/JGAAP) instead.
