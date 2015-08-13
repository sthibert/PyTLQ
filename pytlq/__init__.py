"""
PyTLQ is composed of several modules, each one proposing some functionalities:

* :mod:`ast <pytlq.ast>` defines classes to represent CTL formulas/queries as
  abstract syntax trees.
* :mod:`parser <pytlq.parser>` provides functions to parse strings representing
  CTL queries.
* :mod:`checker <pytlq.checker>` provides functions to check that CTL queries
  belong to syntactic fragment CTLQx.
* :mod:`solver <pytlq.solver>` provides functions to solve CTL queries that
  belong to fragment CTLQx.
* :mod:`simplifier <pytlq.simplifier>` provides functions to simplify the
  solutions returned by the solver.
* :mod:`exception <pytlq.exception>` groups all the PyTLQ-related exceptions.
* :mod:`utils <pytlq.utils>` provides classes and functions used by PyTLQ
  internals, and utilities for manipulating CTL formulas/queries.
"""

__author__ = 'Simon Thibert'
__license__ = 'LGPL-2.1'

__all__ = ['ast', 'parser', 'checker', 'solver', 'simplifier', 'exception',
           'utils']
