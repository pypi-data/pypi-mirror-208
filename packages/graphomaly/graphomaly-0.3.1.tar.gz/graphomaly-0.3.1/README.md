# Graphomaly

Automatic tool for Anti-Money Laundering (AML) and  detecting abnormal behavior in computer networks. Find abnormal data in graph and network structures.

Official package documentation [here](https://unibuc.gitlab.io/graphomaly/graphomaly/).

This work was initially supported by the [Graphomaly Research Grant](http://graphomaly.upb.ro/) and later partially supported by the [Netalert Research Grant](https://cs.unibuc.ro/~pirofti/netalert.html).

## Installation and setup
Install via pip from the [PyPi repository](https://pypi.org/project/graphomaly/):
```
pip install graphomaly
```

or for the latest changes not yet in the official release:
```
pip install git+https://gitlab.com/unibuc/graphomaly/graphomaly
```

Install via docker from the [DockerHub repository](https://hub.docker.com/r/pirofti/graphomaly)
```
docker pull pirofti/graphomaly
```
For using the GPU pull the dedicated image:
```
docker pull pirofti/graphomaly:latest_gpu
```

## Usage

The package follows the [sklearn](https://scikit-learn.org/) API and can be included in your projects via
```
from graphomaly.estimator import GraphomalyEstimator
```
which will provide you with a standard scikit-learn estimator that you can use in your pipeline.

For configuration and tweaks please consult the YAML file for now until documentation matures.

## Development and testing

First clone the repository and change directory to the root of your fresh checkout.

#### 0. Install Prerequisites
Install PyPA’s [build](https://packaging.python.org/en/latest/key_projects/#build):
```
python3 -m pip install --upgrade build
```

#### 1. Build
Inside the Graphomaly directory
```
python -m build
```

#### 2. Virtual Environment

Create a virtual environment with Python:
```
python -m venv venv
```

Activate the environment:
```
source venv/bin/activate
```

For Windows execute instead:
```
venv\Scripts\activate
```

#### 3. Install
Inside the virtual environment execute:
```
pip install dist/graphomaly-*.whl
```

## Running unit tests

First create the results directory:
```
mkdir -p tests/results/synthetic
```

Run the initial test on synthetic data to make sure things installed ok:
```
cd tests && python test_synthetic
```

Then run the other unit tests by hand as above or via `pytest`:

```
pytest  # add -v for verbose, add -s to print(...) to console from tests
```
