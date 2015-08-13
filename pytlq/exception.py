"""
The :mod:`pytlq.exception` module groups all the PyTLQ-related exceptions.
"""

__all__ = ['PyTLQError', 'NoPlaceholderError', 'ValueOutOfBoundsError',
           'VariableNotInModelError']


class PyTLQError(Exception):
    """Base class for PyTLQ exceptions."""
    pass


class NoPlaceholderError(PyTLQError):
    """Exception raised when there is no placeholder in CTL query."""
    pass


class ValueOutOfBoundsError(PyTLQError):
    """Exception raised when the input value is out of bounds."""
    pass


class VariableNotInModelError(PyTLQError):
    """Exception raised when a variable is not present in the model."""
    pass
