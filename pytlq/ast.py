"""
The :mod:`pytlq.ast` module defines classes to represent CTL formulas/queries
as abstract syntax trees.
"""

__all__ = [
    'AST',
    'Placeholder', 'TrueExp', 'FalseExp', 'Atom',
    'Not', 'And', 'Or', 'Imply', 'Iff',
    'AX', 'AF', 'AG', 'AU', 'AW', 'EX', 'EF', 'EG', 'EU', 'EW',
    'AoU', 'AoW', 'AdU', 'AdW', 'EoU', 'EoW', 'EdU', 'EdW'
]

from collections import namedtuple


def _commutative_eq(self_, other):
    """Define equality for commutative operators."""
    return (isinstance(self_, type(other))
            and ((self_.left == other.left and self_.right == other.right)
                 or (self_.left == other.right and self_.right == other.left)))


# =============================================================================
# ==== AST superclass =========================================================
# =============================================================================

class AST(tuple):
    """An abstract syntax tree."""

    # Extend equality to take the "name" of the namedtuple into account.
    def __eq__(self, other):
        return isinstance(self, type(other)) and tuple.__eq__(self, other)

    # There are no implied relationships among the comparison operators in
    # Python (that is, the truth of x==y does not imply that x!=y is false).
    # Therefore, we must also define the __ne__() method.
    def __ne__(self, other):
        return not self.__eq__(other)


# =============================================================================
# ==== Leaves =================================================================
# =============================================================================

class Placeholder(AST, namedtuple('Placeholder', [])):
    """A placeholder."""
    def __str__(self):
        return '?'


class TrueExp(AST, namedtuple('TrueExp', [])):
    """The True constant."""
    def __str__(self):
        return 'True'


class FalseExp(AST, namedtuple('FalseExp', [])):
    """The False constant."""
    def __str__(self):
        return 'False'


class Atom(AST, namedtuple('Atom', ['value'])):
    """An atomic proposition."""
    def __str__(self):
        return "'{value}'".format(value=str(self.value))


# =============================================================================
# ==== Logical operators ======================================================
# =============================================================================

class Not(AST, namedtuple('Not', ['child'])):
    """The ~ (not) operator."""
    def __str__(self):
        return '~({child})'.format(child=str(self.child))


class And(AST, namedtuple('And', ['left', 'right'])):
    """The & (and) operator."""
    def __str__(self):
        return '({left} & {right})'.format(left=str(self.left),
                                           right=str(self.right))

    # Override __eq__ method.
    def __eq__(self, other):
        return _commutative_eq(self, other)


class Or(AST, namedtuple('Or', ['left', 'right'])):
    """The | (or) operator."""
    def __str__(self):
        return '({left} | {right})'.format(left=str(self.left),
                                           right=str(self.right))

    # Override __eq__ method.
    def __eq__(self, other):
        return _commutative_eq(self, other)


class Imply(AST, namedtuple('Imply', ['left', 'right'])):
    """The -> (imply) operator."""
    def __str__(self):
        return '({left} -> {right})'.format(left=str(self.left),
                                            right=str(self.right))


class Iff(AST, namedtuple('Iff', ['left', 'right'])):
    """The <-> (iff) operator."""
    def __str__(self):
        return '({left} <-> {right})'.format(left=str(self.left),
                                             right=str(self.right))

    # Override __eq__ method.
    def __eq__(self, other):
        return _commutative_eq(self, other)


# =============================================================================
# ==== CTL operators ==========================================================
# =============================================================================

class AX(AST, namedtuple('AX', ['child'])):
    """The "next" operator (for all paths)."""
    def __str__(self):
        return 'AX ({child})'.format(child=str(self.child))


class AF(AST, namedtuple('AF', ['child'])):
    """The "eventually" operator (for all paths)."""
    def __str__(self):
        return 'AF ({child})'.format(child=str(self.child))


class AG(AST, namedtuple('AG', ['child'])):
    """The "globally" operator (for all paths)."""
    def __str__(self):
        return 'AG ({child})'.format(child=str(self.child))


class AU(AST, namedtuple('AU', ['left', 'right'])):
    """The "strong until" operator (for all paths)."""
    def __str__(self):
        return 'A[{left} U {right}]'.format(left=str(self.left),
                                            right=str(self.right))


class AW(AST, namedtuple('AW', ['left', 'right'])):
    """The "weak until" operator (for all paths)."""
    def __str__(self):
        return 'A[{left} W {right}]'.format(left=str(self.left),
                                            right=str(self.right))


class EX(AST, namedtuple('EX', ['child'])):
    """The "next" operator (for some path)."""
    def __str__(self):
        return 'EX ({child})'.format(child=str(self.child))


class EF(AST, namedtuple('EF', ['child'])):
    """The "eventually" operator (for some path)."""
    def __str__(self):
        return 'EF ({child})'.format(child=str(self.child))


class EG(AST, namedtuple('EG', ['child'])):
    """The "globally" operator (for some path)."""
    def __str__(self):
        return 'EG ({child})'.format(child=str(self.child))


class EU(AST, namedtuple('EU', ['left', 'right'])):
    """The "strong until" operator (for some path)."""
    def __str__(self):
        return 'E[{left} U {right}]'.format(left=str(self.left),
                                            right=str(self.right))


class EW(AST, namedtuple('EW', ['left', 'right'])):
    """The "weak until" operator (for some path)."""
    def __str__(self):
        return 'E[{left} W {right}]'.format(left=str(self.left),
                                            right=str(self.right))


class AoU(AST, namedtuple('AoU', ['left', 'right'])):
    """The "overlapping strong until" operator (for all paths)."""
    def __str__(self):
        return 'A[{left} oU {right}]'.format(left=str(self.left),
                                             right=str(self.right))


class AoW(AST, namedtuple('AoW', ['left', 'right'])):
    """The "overlapping weak until" operator (for all paths)."""
    def __str__(self):
        return 'A[{left} oW {right}]'.format(left=str(self.left),
                                             right=str(self.right))


class AdU(AST, namedtuple('AdU', ['left', 'right'])):
    """The "disjoint strong until" operator (for all paths)."""
    def __str__(self):
        return 'A[{left} dU {right}]'.format(left=str(self.left),
                                             right=str(self.right))


class AdW(AST, namedtuple('AdW', ['left', 'right'])):
    """The "disjoint weak until" operator (for all paths)."""
    def __str__(self):
        return 'A[{left} dW {right}]'.format(left=str(self.left),
                                             right=str(self.right))


class EoU(AST, namedtuple('EoU', ['left', 'right'])):
    """The "overlapping strong until" operator (for some path)."""
    def __str__(self):
        return 'E[{left} oU {right}]'.format(left=str(self.left),
                                             right=str(self.right))


class EoW(AST, namedtuple('EoW', ['left', 'right'])):
    """The "overlapping weak until" operator (for some path)."""
    def __str__(self):
        return 'E[{left} oW {right}]'.format(left=str(self.left),
                                             right=str(self.right))


class EdU(AST, namedtuple('EdU', ['left', 'right'])):
    """The "disjoint strong until" operator (for some path)."""
    def __str__(self):
        return 'E[{left} dU {right}]'.format(left=str(self.left),
                                             right=str(self.right))


class EdW(AST, namedtuple('EdW', ['left', 'right'])):
    """The "disjoint weak until" operator (for some path)."""
    def __str__(self):
        return 'E[{left} dW {right}]'.format(left=str(self.left),
                                             right=str(self.right))
