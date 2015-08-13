"""
The :mod:`pytlq.parser` module provides functions to parse strings representing
CTL queries.
"""

__all__ = ['parse_ctlq']

from pyparsing import Forward, Literal, SkipTo, Suppress, ZeroOrMore

from .ast import (Placeholder, TrueExp, FalseExp, Atom, Not, And, Or, Imply,
                  Iff, AX, AF, AG, AU, AW, EX, EF, EG, EU, EW, AoU, AoW, AdU,
                  AdW, EoU, EoW, EdU, EdW)
from .utils import count_placeholders
from .exception import NoPlaceholderError


def _left(class_, tokens):
    """
    Parse `tokens` and return an AST, assuming left associativity.

    Given a list of tokens [v1, op, v2, op, ..., op, vn], return res, a
    hierarchy of instances of `class_` such that:
        res = class_(class_(...class_(v1, v2), ..., vn)

    .. note:: This is a helper function to parse logical operators.
    .. credit:: Written by Simon Busard.
    """
    if len(tokens) == 1:
        return tokens[0]
    else:
        return class_(_left(class_, tokens[:-2]), tokens[-1])


def _right(class_, tokens):
    """
    Parse `tokens` and return an AST, assuming right associativity.

    Given a list of tokens [v1, op, v2, op, ..., op, vn], return res, a
    hierarchy of instances of `class_` such that:
        res = class_(v1, class_(v2, ..., vn)...)

    .. note:: This is a helper function to parse logical operators.
    .. credit:: Written by Simon Busard.
    """
    if len(tokens) == 1:
        return tokens[0]
    else:
        return class_(tokens[0], _right(class_, tokens[2:]))


def _logical_parser(expression):
    """
    Return a new parser parsing logical expressions.

    This parser recognizes the following grammar, with precedence:

    <logical> ::= expression | '~' <logical> | <logical> '&' <logical>
                | <logical> '|' <logical> | <logical> '->' <logical>
                | <logical> '<->' <logical>

    .. note:: The parser uses :mod:`pytlq.ast` module's classes to build ASTs.
    .. credit:: Adapted from Simon Busard's parser parsing logical expressions
        on atomics.
    """
    parser = Forward()

    not_strict = Literal('~') + expression
    not_strict.setParseAction(lambda tokens: Not(tokens[1]))
    not_ = (not_strict | expression)
    and_ = not_ + ZeroOrMore(Literal('&') + not_)
    and_.setParseAction(lambda tokens: _left(And, tokens))
    or_ = and_ + ZeroOrMore(Literal('|') + and_)
    or_.setParseAction(lambda tokens: _left(Or, tokens))
    imply = ZeroOrMore(or_ + Literal('->')) + or_
    imply.setParseAction(lambda tokens: _right(Imply, tokens))
    iff = imply + ZeroOrMore(Literal('<->') + imply)
    iff.setParseAction(lambda tokens: _left(Iff, tokens))

    parser <<= iff

    return parser


def _ctlq_parser():
    """
    Return a new parser parsing CTL queries.

    This parser recognizes the following grammar:

    <ctlq> ::= '?' | 'True' | 'False' | <atom> | '~' <ctlq> | <ctlq> '&' <ctlq>
            | <ctlq> '|' <ctlq> | <ctlq> '->' <ctlq> | <ctlq> '<->' <ctlq>
            | 'A' 'X' <ctlq> | 'E' 'X' <ctlq> | 'A' 'F' <ctlq>
            | 'E' 'F' <ctlq> | 'A' 'G' <ctlq> | 'E' 'G' <ctlq>
            | 'A' '[' <ctlq> 'U' <ctlq> ']' | 'E' '[' <ctlq> 'U' <ctlq> ']'
            | 'A' '[' <ctlq> 'W' <ctlq> ']' | 'E' '[' <ctlq> 'W' <ctlq> ']'
            | 'A' '[' <ctlq> 'oU' <ctlq> ']' | 'E' '[' <ctlq> 'oU' <ctlq> ']'
            | 'A' '[' <ctlq> 'oW' <ctlq> ']' | 'E' '[' <ctlq> 'oW' <ctlq> ']'
            | 'A' '[' <ctlq> 'dU' <ctlq> ']' | 'E' '[' <ctlq> 'dU' <ctlq> ']'
            | 'A' '[' <ctlq> 'dW' <ctlq> ']' | 'E' '[' <ctlq> 'dW' <ctlq> ']'

    <atom> is defined by any string surrounded by single quotes.

    .. note:: The parser uses :mod:`pytlq.ast` module's classes to build ASTs.
    """
    parser = Forward()

    # Ignore parentheses.
    parentheses = Suppress('(') + parser + Suppress(')')

    # Parse propositions.
    placeholder = Literal('?')
    placeholder.setParseAction(lambda tokens: Placeholder())
    true = Literal('True')
    true.setParseAction(lambda tokens: TrueExp())
    false = Literal('False')
    false.setParseAction(lambda tokens: FalseExp())
    atom = Literal("'") + SkipTo("'") + Literal("'")
    atom.setParseAction(lambda tokens: Atom(tokens[1]))

    proposition = (placeholder | true | false | atom)

    # Variable used to define correct precedence of unary temporal operators X,
    # F, and G (that is, higher than logical operators).
    expression = Forward()

    # Parse CTL operators.
    ax = Literal('A') + Literal('X') + expression
    ax.setParseAction(lambda tokens: AX(tokens[2]))
    ex = Literal('E') + Literal('X') + expression
    ex.setParseAction(lambda tokens: EX(tokens[2]))
    af = Literal('A') + Literal('F') + expression
    af.setParseAction(lambda tokens: AF(tokens[2]))
    ef = Literal('E') + Literal('F') + expression
    ef.setParseAction(lambda tokens: EF(tokens[2]))
    ag = Literal('A') + Literal('G') + expression
    ag.setParseAction(lambda tokens: AG(tokens[2]))
    eg = Literal('E') + Literal('G') + expression
    eg.setParseAction(lambda tokens: EG(tokens[2]))
    au = (Literal('A') + Literal('[') + parser + Literal('U') + parser
          + Literal(']'))
    au.setParseAction(lambda tokens: AU(tokens[2], tokens[4]))
    eu = (Literal('E') + Literal('[') + parser + Literal('U') + parser
          + Literal(']'))
    eu.setParseAction(lambda tokens: EU(tokens[2], tokens[4]))
    aw = (Literal('A') + Literal('[') + parser + Literal('W') + parser
          + Literal(']'))
    aw.setParseAction(lambda tokens: AW(tokens[2], tokens[4]))
    ew = (Literal('E') + Literal('[') + parser + Literal('W') + parser
          + Literal(']'))
    ew.setParseAction(lambda tokens: EW(tokens[2], tokens[4]))
    aou = (Literal('A') + Literal('[') + parser + Literal('oU') + parser
           + Literal(']'))
    aou.setParseAction(lambda tokens: AoU(tokens[2], tokens[4]))
    eou = (Literal('E') + Literal('[') + parser + Literal('oU') + parser
           + Literal(']'))
    eou.setParseAction(lambda tokens: EoU(tokens[2], tokens[4]))
    aow = (Literal('A') + Literal('[') + parser + Literal('oW') + parser
           + Literal(']'))
    aow.setParseAction(lambda tokens: AoW(tokens[2], tokens[4]))
    eow = (Literal('E') + Literal('[') + parser + Literal('oW') + parser
           + Literal(']'))
    eow.setParseAction(lambda tokens: EoW(tokens[2], tokens[4]))
    adu = (Literal('A') + Literal('[') + parser + Literal('dU') + parser
           + Literal(']'))
    adu.setParseAction(lambda tokens: AdU(tokens[2], tokens[4]))
    edu = (Literal('E') + Literal('[') + parser + Literal('dU') + parser
           + Literal(']'))
    edu.setParseAction(lambda tokens: EdU(tokens[2], tokens[4]))
    adw = (Literal('A') + Literal('[') + parser + Literal('dW') + parser
           + Literal(']'))
    adw.setParseAction(lambda tokens: AdW(tokens[2], tokens[4]))
    edw = (Literal('E') + Literal('[') + parser + Literal('dW') + parser
           + Literal(']'))
    edw.setParseAction(lambda tokens: EdW(tokens[2], tokens[4]))

    temporal = (ax | ex | af | ef | ag | eg | au | eu | aw | ew | aou | eou
                | aow | eow | adu | edu | adw | edw)

    formula = (parentheses | proposition | temporal)

    not_formula = Literal('~') + formula
    not_formula.setParseAction(lambda tokens: Not(tokens[1]))

    expression <<= (formula | not_formula)

    # Parse logical operators, with precedence and associativity.
    logical = _logical_parser(expression)

    # The complete CTL parser.
    parser <<= logical

    return parser


# Variable used to store parser instance to avoid redefining it unnecessarily.
_ctlq = None


def parse_ctlq(query):
    """
    Parse `query` and return its corresponding AST.

    :param query: a string representing a CTL query (that is, a CTL formula
        where some subformulas are replaced by the special symbol ``?``, called
        placeholder)
    :return: an AST-based CTL query

    :raise: a :exc:`pyparsing.ParseException` if a parsing error occurs
    :raise: a :exc:`pytlq.exception.NoPlaceholderError` if `query` does not
        contain any placeholder

    .. note:: The parser uses :mod:`pytlq.ast` module's classes to build ASTs.
    """
    global _ctlq
    if _ctlq is None:
        # Create the CTLQ parser.
        _ctlq = _ctlq_parser()

    # The parser is assumed to return a one-element list when parsing a string.
    ast = _ctlq.parseString(query, parseAll=True)[0]

    # There must be at least one occurrence of the placeholder in the AST,
    # otherwise it does not represent a CTL query.
    if count_placeholders(ast) < 1:
        raise NoPlaceholderError('{query} does not contain any placeholder'
                                 .format(query=query))

    return ast
