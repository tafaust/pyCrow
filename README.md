<img src='./resources/raven-576679_960_720.png' height="150px" align="left" padding="0" margin="0">


<h1>pyCrow:<br />A Python 3.6 speech recognition framework.</h1>

Welcome to the pyCrow speech recognition project!
The main purpose of this project is, first, to keep up with Machine Learning and Python and, second, to teach myself about Deep Learning in my free time.
More specifically, I aim to learn about Long-Short Term Memory (LSTM) Neural Networks (NN). In case you are interested to hear more about the project, give me feedback on the code, or even want to contribute to this project, feel free to send me a PM (or PR).
Thanks!


Note that I will use **$** and **#** in bash code examples to signal the required privileges.

## Installation
Checkout this git repository first.
Then, make sure you have Python3.6 and virtualenv installed in order to create a virtual environment based on Python 3.6.

    $ git clone git@github.com:tahesse/pyCrow.git && cd ./pyCrow
    $ virtualenv -p python3.6 venv

Next, activate the virtualenv install the required python packages via pip.

    $ source ./venv/bin/activate
    $ pip install -r requirements.txt

Finally, you will need a `redis` Message Broker running. The suggested installation is via `docker`. Make sure to have the `docker` daemon running and install `redis` by typing the following in your console

    # docker run --name crow-redis -d -p 6379:6379 redis

By now, you should have the framework installed and be able to start it. If not, please open up an issue for that.

## Getting Started
TBD

## Documentation
TBD

## Examples
TBD

---
# Auxiliary information

MFCC-standardized algorithm:
* http://www.etsi.org/deliver/etsi_es/201100_201199/201108/01.01.03_60/es_201108v010103p.pdf

CC0-licensed images taken from:
* https://pixabay.com/en/raven-head-bird-black-feather-576679/
* https://pixabay.com/en/crow-hanging-pendant-taxidermy-575836/
