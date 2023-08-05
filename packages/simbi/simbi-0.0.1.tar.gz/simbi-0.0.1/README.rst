.. figure:: docs/images/simbi_logo.jpg

SimBi: Simulating Bimodal Atom Clouds 
=============================================================

`Quickstart <#quickstart-colab-in-the-cloud>`__ \| `Install
guide <#installation>`__ \| `API Docs <https://simbi.readthedocs.io/>`__

What is SimBi?
---------------

Simbi allows ultracold atom clouds to be simulated after 
time-of-flight expansion. This includes thermal clouds, 
Bose-Einstein condensates or a mixture of the two. 
This package was created to generate simulated 
datasets of ultracold atom cloud images. These 
simulated datasets can then be used to train deep 
neural networks.

Currently the package only relies on Numpy and Scipy,
although in the future the functions will be calculated 
with JAX which will allow for GPU speedups. 

Contents
~~~~~~~~

-  `Quickstart: Colab in the Cloud <#quickstart-colab-in-the-cloud>`__
-  `Installation <#installation>`__
-  `Reference documentation <https://simbi.readthedocs.io/>`__

Quickstart: Colab in the Cloud
------------------------------

The easiest way to test out SimBi is using a Colab notebook. 
We have a few tutorial notebooks including: 

- `The basics: simulating atom clouds with SimBi <https://colab.research.google.com/github/lucashofer/simbi/blob/main/docs/notebooks/SimBi_Quickstart.ipynb>`__
- `Solving for chemical potential and temperature <https://colab.research.google.com/github/lucashofer/simbi/blob/main/docs/notebooks/SimBi_Solve.ipynb>`__


Installation
------------

SimBi is written in Python and can be installed via pip

::

   pip install simbi

API Documentation
-----------------------

For details about the SimBi API, see the `reference documentation <https://simbi.readthedocs.io/>`__.