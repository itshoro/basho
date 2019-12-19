# BASHO
BASHO is a mockup of a pax-counting application, served as a distributed system, consisting of multiple backend services and a client application, as well as an API for data submission.

**To cut down on development time devices are emulated.**

## Installation
To run BASHO on a single system it is required to run it in a virtual environment for the moment (or install the util package globally).

```shell
# Setup virtual environment
python -m venv ENV_NAME
./ENV_NAME/Scripts/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```