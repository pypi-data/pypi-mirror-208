## SciCom

Simulating various aspects of scientific communication via Agent-based models.

In this first version, we introduce an agent-based modelling approach to reconstruct communication in
the Republic of Letters.

Documentation is available on [ReadTheDocs](https://scientificcommunication.readthedocs.io).

## Installation

tl;dr Use pip

~~~bash
pip install scicom
~~~

Consider using a clean virtual environment to keep your main packages separated.
Create a new virtual environment and install the package

~~~bash
python3 -m venv env
source env/bin/activate
pip install scicom
~~~

## Examples

You can find an example Jupyter Notebook showing the use of the LetterSpace model in the [examples folder](./examples/RunModel.ipynb). 

Alternatively, you can use the mesa server framework to create an local browser interface with changeable parameters, 
see screenshot below and [documentation on running mesa](./docs/usingmesa.rst).
<img src="./docs/letterModel.png" alt= “MesaInterface” width="800" height="400">


## Testing

Tests can be run by installing the _dev_ requirements and running `tox`.

~~~bash
pip install scicom[dev]
tox
~~~

## Building documentation

The documentation is build using _sphinx_. Install with the _dev_ option and run

~~~bash
pip install scicom[dev]
tox -e docs
~~~

## Funding information

The development is part of the research project [ModelSEN](https://modelsen.mpiwg-berlin.mpg.de)

> Socio-epistemic networks: Modelling Historical Knowledge Processes,

in Department I of the Max Planck Institute for the History of Science
and funded by the Federal Ministry of Education and Research, Germany (Grant No. 01 UG2131).
