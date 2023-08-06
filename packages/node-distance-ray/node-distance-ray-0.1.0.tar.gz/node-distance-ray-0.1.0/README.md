[![PyPI version](https://badge.fury.io/py/node-distance-ray.svg)](https://badge.fury.io/py/node-distance-ray)
[![PyPi downloads](https://img.shields.io/pypi/dm/node-distance-ray)](https://img.shields.io/pypi/dm/)

# node-distance-ray
[ray.io](https://www.ray.io/) wrapper for [node-distance](https://github.com/satzbeleg/node-distance) package.


## Usage
see test/test_.py


## Appendix

### Installation
The `node-distance-ray` [git repo](http://github.com/satzbeleg/node-distance-ray) is available as [PyPi package](https://pypi.org/project/node-distance-ray)

```sh
pip install node-distance-ray
pip install git+ssh://git@github.com/satzbeleg/node-distance-ray.git
```

### Install a virtual environment

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
pip install -r requirements-dev.txt --no-cache-dir
```

(If your git repo is stored in a folder with whitespaces, then don't use the subfolder `.venv`. Use an absolute path without whitespaces.)

### Python commands

* Jupyter for the examples: `jupyter lab`
* Check syntax: `flake8 --ignore=F401 --exclude=$(grep -v '^#' .gitignore | xargs | sed -e 's/ /,/g')`
* Run Unit Tests: `PYTHONPATH=. pytest`

Publish

```sh
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
Please [open an issue](https://github.com/satzbeleg/node-distance-ray/issues/new) for support.


### Contributing
Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/satzbeleg/node-distance-ray/compare/).
