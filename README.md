PyTLQ: A Python Package for Solving Temporal Logic Queries
==========================================================

PyTLQ is an original Python package for solving temporal logic queries, as 
defined by Chan [1] and corrected/extended by Samer and Veith [2, 3].

Temporal logic query solving is an extension of model checking whose main aim 
is to understand a model as opposed to merely verifying its correctness. A 
temporal logic query basically consists of a temporal logic formula where 
some subformulas are replaced by the special symbol `?` representing a "hole" 
in the formula. The query solving problem then consists of finding the right 
subformula to fill the hole(s) and make the initial formula satisfied in the 
considered modeled system.

PyTLQ can therefore be seen as an extension of the PyNuSMV model-checking 
library [4]. Within this framework, it uses the BDD-based model checking 
functionalities of the latter to efficiently implement temporal logic queries.


Dependencies
------------

- PyNuSMV - http://lvl.info.ucl.ac.be/Tools/PyNuSMV
- PyParsing - http://pyparsing.wikispaces.com
- Click - http://click.pocoo.org


Installation
------------

*Remark. Make sure you are using Python 3 before installing PyTLQ.*

    $ pip install https://github.com/sthibert/PyTLQ/zipball/master

Note that PyParsing and Click are **automatically** installed with PyTLQ, but 
PyNuSMV must be **manually** installed before using PyTLQ.


Usage
-----

PyTLQ is meant to be called from the command line. The usage is:

    $ pytlq <model_path> <query> [--order <order_path>]

- `<model_path>` represents the path to the SMV model you want to analyse.
- `<query>` represents your CTL query as a string (see Documentation for the 
  syntax of the input language).
- `<order_path>` is an optional argument that allows you to provide an order 
  file (.ord) to PyTLQ, in order to compute the considered SMV model 
  efficiently.

This command computes the unique set of solution states that represents an 
exact solution to `query` in the system defined in `model_path` (if there is 
one). Then, you have the choice of projecting the solution on a subset of the 
variables of the system, simplifying the solution thanks to an approximate 
conjunctive decomposition, or you can quit PyTLQ.

To display the usage instructions, just enter:

    $ pytlq --help


Documentation
-------------

The full documentation can be found on:

    docs/html/index.html


License
-------

PyTLQ is licensed under the GNU Lesser General Public License version 2.1. File 
LICENSE.txt contains a copy of the license.


References
----------

[1] Chan, William. "Temporal-Logic Queries." Computer Aided Verification. 
Springer Berlin Heidelberg, 2000.

[2] Samer, Marko, and Helmut Veith. "Validity of CTL Queries Revisited." 
Computer Science Logic. Springer Berlin Heidelberg, 2003.

[3] Samer, Marko, and Helmut Veith. "Deterministic CTL Query Solving." 
Temporal Representation and Reasoning, 2005. TIME 2005. 12th International 
Symposium on. IEEE, 2005.

[4] Busard, Simon, and Charles Pecheur. "PyNuSMV: NuSMV as a Python Library."
NASA Formal Methods. Springer Berlin Heidelberg, 2013.
