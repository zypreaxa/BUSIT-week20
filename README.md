# BUSIT-week20
## Team domain - Posession
## Installation steps
### Prerequisites
Before starting, you should make sure the appropriate version of python is installed in your device. The version this project is based on is *Python 3.10*. To check which version you have you can run 
```
python --version
```
If the version in the output is _NOT_ 3.10, you should download it using this link: https://www.python.org/downloads/release/python-3100/
### Setting up the environment 
After cloning the repository, run
```
python -m venv venv 
```
to create a virtual environment, then run
```
venv/scripts/activate
```
to activate the environment.

### Installing the requirements
To install all dependencies, run
```
pip install -r requirements.txt
```
If any new dependencies are added in later distributions, you will need to run the command above again.

## Initializing the submodule
If the submodule folders appear empty, an initialization will be needed.
To initialize the submodule run: 
```
git submodule update --init --recursive
```
---
## Basic project structure
This repository consists of two submodules that were used as resources and the model. The submodules are not required for the model to run. The model can be accessed in the notebooks/---.ipynb file.




