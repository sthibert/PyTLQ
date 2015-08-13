"""
The :mod:`pytlq.checker` module provides functions to check that CTL queries
belong to syntactic fragment CTLQx.
"""

__all__ = ['check_ctlqx', 'non_terminal_ctlqx']

from .utils import count_placeholders, path_to_placeholder


# Production rules of syntactic fragment CTLQx (adapted from Samer and Veith's
# definition at TIME'05):
#
# <ctlqx> ::= <q1> | <q2> | <q3> | <q4> | <q5> | <q6> | <q7> | <q8> | <q9>
#           | <q10>
#
# <q1> ::= '?' | '~' '?' | <ctl> '&' <q1> | <ctl> '&' <q3> | <ctl> '&' <q4>
#        | <ctl> '|' <q1> | <ctl> '|' <q2> | 'A' 'X' <q1> | 'A' 'X' <q3>
#        | 'A' 'X' <q4> | 'A' 'X' <q6> | 'A' 'X' <q7>
#        | 'A' '[' <q1> 'oU' <ctl> ']' | 'A' '[' <q3> 'oU' <ctl> ']'
#        | 'A' '[' <q4> 'oU' <ctl> ']' | 'A' '[' <ctl> 'oU' <q4> ']'
#        | 'A' '[' <ctl> 'oU' <q5> ']' | 'A' '[' <ctl> 'dU' <q1> ']'
#        | 'A' '[' <ctl> 'dU' <q2> ']' | 'A' '[' <ctl> 'dU' <q3> ']'
#        | 'A' '[' <ctl> 'dU' <q4> ']' | 'A' '[' <ctl> 'dU' <q5> ']'
#        | 'A' '[' <q1> 'oW' <ctl> ']' | 'A' '[' <q3> 'oW' <ctl> ']'
#        | 'A' '[' <q4> 'oW' <ctl> ']' | 'A' '[' <ctl> 'dW' <q1> ']'
#        | 'A' '[' <ctl> 'dW' <q2> ']' | 'A' '[' <ctl> 'dW' <q3> ']'
#        | 'A' '[' <ctl> 'dW' <q4> ']' | 'A' '[' <ctl> 'dW' <q5> ']'
#
# <q2> ::= <ctl> '&' <q2> | <ctl> '&' <q5> | 'A' 'X' <q2> | 'A' 'X' <q5>
#        | 'A' '[' <q2> 'oU' <ctl> ']' | 'A' '[' <q5> 'oU' <ctl> ']'
#        | 'A' '[' <ctl> 'oU' <q3> ']' | 'A' '[' <q2> 'oW' <ctl> ']'
#        | 'A' '[' <q5> 'oW' <ctl> ']' | 'A' '[' <ctl> 'oW' <q3> ']'
#        | 'A' '[' <ctl> 'oW' <q4> ']' | 'A' '[' <ctl> 'oW' <q5> ']'
#
# <q3> ::= <ctl> '|' <q3> | 'A' 'F' <q3> | 'A' 'F' <q6>
#        | 'A' '[' <q1> 'U' <ctl> ']' | 'A' '[' <q2> 'U' <ctl> ']'
#        | 'A' '[' <q3> 'U' <ctl> ']' | 'A' '[' <q4> 'U' <ctl> ']'
#        | 'A' '[' <q5> 'U' <ctl> ']' | 'A' '[' <q6> 'U' <ctl> ']'
#        | 'A' '[' <q7> 'U' <ctl> ']' | 'A' '[' <ctl> 'U' <q3> ']'
#        | 'A' '[' <ctl> 'U' <q6> ']'
#
# <q4> ::= <ctl> '|' <q4> | <ctl> '|' <q5> | 'A' 'F' <q4> | 'A' 'F' <q5>
#        | 'A' 'F' <q7> | 'A' '[' <q6> 'oU' <ctl> ']'
#        | 'A' '[' <q7> 'oU' <ctl> ']' | 'A' '[' <ctl> 'U' <q4> ']'
#        | 'A' '[' <ctl> 'U' <q5> ']' | 'A' '[' <ctl> 'U' <q7> ']'
#        | 'A' '[' <ctl> 'oU' <q7> ']' | 'A' '[' <ctl> 'dU' <q6> ']'
#        | 'A' '[' <ctl> 'dU' <q7> ']' | 'A' '[' <q1> 'W' <ctl> ']'
#        | 'A' '[' <q2> 'W' <ctl> ']' | 'A' '[' <q3> 'W' <ctl> ']'
#        | 'A' '[' <q4> 'W' <ctl> ']' | 'A' '[' <q5> 'W' <ctl> ']'
#        | 'A' '[' <q6> 'W' <ctl> ']' | 'A' '[' <q7> 'W' <ctl> ']'
#        | 'A' '[' <q6> 'oW' <ctl> ']' | 'A' '[' <q7> 'oW' <ctl> ']'
#        | 'A' '[' <ctl> 'W' <q3> ']' | 'A' '[' <ctl> 'W' <q4> ']'
#        | 'A' '[' <ctl> 'W' <q5> ']' | 'A' '[' <ctl> 'W' <q6> ']'
#        | 'A' '[' <ctl> 'W' <q7> ']' | 'A' '[' <ctl> 'dW' <q6> ']'
#        | 'A' '[' <ctl> 'dW' <q7> ']'
#
# <q5> ::= 'A' '[' <ctl> 'oU' <q6> ']' | 'A' '[' <ctl> 'oW' <q6> ']'
#        | 'A' '[' <ctl> 'oW' <q7> ']'
#
# <q6> ::= <ctl> '|' <q6> | 'A' '[' <q8> 'U' <ctl> ']'
#        | 'A' '[' <q9> 'U' <ctl> ']'
#
# <q7> ::= <ctl> '&' <q6> | <ctl> '&' <q7> | <ctl> '|' <q7> | <ctl> '|' <q8>
#        | <ctl> '|' <q9> | 'A' '[' <q8> 'W' <ctl> ']'
#        | 'A' '[' <q9> 'W' <ctl> ']'
#
# <q8> ::= <ctl> '&' <q8> | 'A' 'X' <q8> | 'A' 'F' <q8> | 'A' 'F' <q9>
#        | 'A' 'G' <q1> | 'A' 'G' <q3> | 'A' 'G' <q4> | 'A' 'G' <q6>
#        | 'A' 'G' <q7> | 'A' 'G' <q8> | 'A' '[' <ctl> 'U' <q8> ']'
#        | 'A' '[' <ctl> 'U' <q9> ']' | 'A' '[' <ctl> 'oU' <q8> ']'
#        | 'A' '[' <ctl> 'oU' <q9> ']' | 'A' '[' <ctl> 'dU' <q8> ']'
#        | 'A' '[' <ctl> 'dU' <q9> ']' | 'A' '[' <ctl> 'W' <q8> ']'
#        | 'A' '[' <ctl> 'W' <q9> ']' | 'A' '[' <ctl> 'dW' <q8> ']'
#        | 'A' '[' <ctl> 'dW' <q9> ']' | 'A' '[' <q8> 'oU' <ctl> ']'
#        | 'A' '[' <q8> 'oW' <ctl> ']'
#
# <q9> ::= <ctl> '&' <q9> | 'A' 'X' <q9> | 'A' '[' <ctl> 'oW' <q8> ']'
#        | 'A' '[' <ctl> 'oW' <q9> ']' | 'A' '[' <q9> 'oU' <ctl> ']'
#        | 'A' '[' <q9> 'oW' <ctl> ']'
#
# <q10> ::= <ctl> '&' <q10> | <ctl> '|' <q10> | 'A' 'X' <q10> | 'A' 'F' <q10>
#         | 'A' 'G' <q2> | 'A' 'G' <q5> | 'A' 'G' <q9> | 'A' 'G' <q10>
#         | 'A' '[' <q10> 'U' <ctl> ']' | 'A' '[' <q10> 'oU' <ctl> ']'
#         | 'A' '[' <ctl> 'U' <q10> ']' | 'A' '[' <ctl> 'oU' <q10> ']'
#         | 'A' '[' <ctl> 'dU' <q10> ']' | 'A' '[' <q10> 'W' <ctl> ']'
#         | 'A' '[' <q10> 'oW' <ctl> ']' | 'A' '[' <ctl> 'W' <q10> ']'
#         | 'A' '[' <ctl> 'oW' <q10> ']' | 'A' '[' <ctl> 'dW' <q10> ']'
#
# <ctl> ::= 'True' | 'False' | <atom> | '~' <ctl> | <ctl> '&' <ctl>
#         | <ctl> '|' <ctl> | <ctl> '->' <ctl> | <ctl> '<->' <ctl>
#         | 'A' 'X' <ctl> | 'E' 'X' <ctl> | 'A' 'F' <ctl>
#         | 'E' 'F' <ctl> | 'A' 'G' <ctl> | 'E' 'G' <ctl>
#         | 'A' '[' <ctl> 'U' <ctl> ']' | 'E' '[' <ctl> 'U' <ctl> ']'
#         | 'A' '[' <ctl> 'W' <ctl> ']' | 'E' '[' <ctl> 'W' <ctl> ']'
#         | 'A' '[' <ctl> 'oU' <ctl> ']' | 'E' '[' <ctl> 'oU' <ctl> ']'
#         | 'A' '[' <ctl> 'oW' <ctl> ']' | 'E' '[' <ctl> 'oW' <ctl> ']'
#         | 'A' '[' <ctl> 'dU' <ctl> ']' | 'E' '[' <ctl> 'dU' <ctl> ']'
#         | 'A' '[' <ctl> 'dW' <ctl> ']' | 'E' '[' <ctl> 'dW' <ctl> ']'
#
# <atom> is defined by any string surrounded by single quotes.


def non_terminal_ctlqx(query):
    """
    Return the number of the non-terminal (defined in the production rules,
    adapted from Samer and Veith's definition at TIME'05) in which `query`
    stands if `query` belongs to fragment CTLQx, 0 otherwise.

    :param query: an AST-based CTL query **with exactly one occurrence of the
        placeholder**
    :return: a number between 1 and 10 (representing a non-terminal) if `query`
        belongs to fragment CTLQx, 0 otherwise

    .. note:: See :func:`pytlq.utils.count_placeholders` for the verification
        that `query` contains exactly one occurrence of the placeholder.
    """
    path = path_to_placeholder(query)[::-1]  # Reverse the path.
    non_terminal = 0  # Initialize the non-terminal number to 0.

    for index, element in enumerate(path):
        if element == 'Placeholder':
            non_terminal = 1

        elif element == 'Not':
            if index == 1:
                non_terminal = 1
            else:
                non_terminal = 0
                break

        elif element in ('_And', 'And_'):
            if non_terminal == 1:
                non_terminal = 1
            elif non_terminal == 2:
                non_terminal = 2
            elif non_terminal == 3:
                non_terminal = 1
            elif non_terminal == 4:
                non_terminal = 1
            elif non_terminal == 5:
                non_terminal = 2
            elif non_terminal == 6:
                non_terminal = 7
            elif non_terminal == 7:
                non_terminal = 7
            elif non_terminal == 8:
                non_terminal = 8
            elif non_terminal == 9:
                non_terminal = 9
            elif non_terminal == 10:
                non_terminal = 10

        elif element in ('_Or', 'Or_'):
            if non_terminal == 1:
                non_terminal = 1
            elif non_terminal == 2:
                non_terminal = 1
            elif non_terminal == 3:
                non_terminal = 3
            elif non_terminal == 4:
                non_terminal = 4
            elif non_terminal == 5:
                non_terminal = 4
            elif non_terminal == 6:
                non_terminal = 6
            elif non_terminal == 7:
                non_terminal = 7
            elif non_terminal == 8:
                non_terminal = 7
            elif non_terminal == 9:
                non_terminal = 7
            elif non_terminal == 10:
                non_terminal = 10

        elif element == 'AX':
            if non_terminal == 1:
                non_terminal = 1
            elif non_terminal == 2:
                non_terminal = 2
            elif non_terminal == 3:
                non_terminal = 1
            elif non_terminal == 4:
                non_terminal = 1
            elif non_terminal == 5:
                non_terminal = 2
            elif non_terminal == 6:
                non_terminal = 1
            elif non_terminal == 7:
                non_terminal = 1
            elif non_terminal == 8:
                non_terminal = 8
            elif non_terminal == 9:
                non_terminal = 9
            elif non_terminal == 10:
                non_terminal = 10

        elif element == 'AF':
            if non_terminal == 1:
                non_terminal = 0
                break
            elif non_terminal == 2:
                non_terminal = 0
                break
            elif non_terminal == 3:
                non_terminal = 3
            elif non_terminal == 4:
                non_terminal = 4
            elif non_terminal == 5:
                non_terminal = 4
            elif non_terminal == 6:
                non_terminal = 3
            elif non_terminal == 7:
                non_terminal = 4
            elif non_terminal == 8:
                non_terminal = 8
            elif non_terminal == 9:
                non_terminal = 8
            elif non_terminal == 10:
                non_terminal = 10

        elif element == 'AG':
            if non_terminal == 1:
                non_terminal = 8
            elif non_terminal == 2:
                non_terminal = 10
            elif non_terminal == 3:
                non_terminal = 8
            elif non_terminal == 4:
                non_terminal = 8
            elif non_terminal == 5:
                non_terminal = 10
            elif non_terminal == 6:
                non_terminal = 8
            elif non_terminal == 7:
                non_terminal = 8
            elif non_terminal == 8:
                non_terminal = 8
            elif non_terminal == 9:
                non_terminal = 10
            elif non_terminal == 10:
                non_terminal = 10

        elif element == '_AU':
            if non_terminal == 1:
                non_terminal = 3
            elif non_terminal == 2:
                non_terminal = 3
            elif non_terminal == 3:
                non_terminal = 3
            elif non_terminal == 4:
                non_terminal = 3
            elif non_terminal == 5:
                non_terminal = 3
            elif non_terminal == 6:
                non_terminal = 3
            elif non_terminal == 7:
                non_terminal = 3
            elif non_terminal == 8:
                non_terminal = 6
            elif non_terminal == 9:
                non_terminal = 6
            elif non_terminal == 10:
                non_terminal = 10

        elif element == 'AU_':
            if non_terminal == 1:
                non_terminal = 0
                break
            elif non_terminal == 2:
                non_terminal = 0
                break
            elif non_terminal == 3:
                non_terminal = 3
            elif non_terminal == 4:
                non_terminal = 4
            elif non_terminal == 5:
                non_terminal = 4
            elif non_terminal == 6:
                non_terminal = 3
            elif non_terminal == 7:
                non_terminal = 4
            elif non_terminal == 8:
                non_terminal = 8
            elif non_terminal == 9:
                non_terminal = 8
            elif non_terminal == 10:
                non_terminal = 10

        elif element == '_AW':
            if non_terminal == 1:
                non_terminal = 4
            elif non_terminal == 2:
                non_terminal = 4
            elif non_terminal == 3:
                non_terminal = 4
            elif non_terminal == 4:
                non_terminal = 4
            elif non_terminal == 5:
                non_terminal = 4
            elif non_terminal == 6:
                non_terminal = 4
            elif non_terminal == 7:
                non_terminal = 4
            elif non_terminal == 8:
                non_terminal = 7
            elif non_terminal == 9:
                non_terminal = 7
            elif non_terminal == 10:
                non_terminal = 10

        elif element == 'AW_':
            if non_terminal == 1:
                non_terminal = 0
                break
            elif non_terminal == 2:
                non_terminal = 0
                break
            elif non_terminal == 3:
                non_terminal = 4
            elif non_terminal == 4:
                non_terminal = 4
            elif non_terminal == 5:
                non_terminal = 4
            elif non_terminal == 6:
                non_terminal = 4
            elif non_terminal == 7:
                non_terminal = 4
            elif non_terminal == 8:
                non_terminal = 8
            elif non_terminal == 9:
                non_terminal = 8
            elif non_terminal == 10:
                non_terminal = 10

        elif element == '_AoU':
            if non_terminal == 1:
                non_terminal = 1
            elif non_terminal == 2:
                non_terminal = 2
            elif non_terminal == 3:
                non_terminal = 1
            elif non_terminal == 4:
                non_terminal = 1
            elif non_terminal == 5:
                non_terminal = 2
            elif non_terminal == 6:
                non_terminal = 4
            elif non_terminal == 7:
                non_terminal = 4
            elif non_terminal == 8:
                non_terminal = 8
            elif non_terminal == 9:
                non_terminal = 9
            elif non_terminal == 10:
                non_terminal = 10

        elif element == 'AoU_':
            if non_terminal == 1:
                non_terminal = 0
                break
            elif non_terminal == 2:
                non_terminal = 0
                break
            elif non_terminal == 3:
                non_terminal = 2
            elif non_terminal == 4:
                non_terminal = 1
            elif non_terminal == 5:
                non_terminal = 1
            elif non_terminal == 6:
                non_terminal = 5
            elif non_terminal == 7:
                non_terminal = 4
            elif non_terminal == 8:
                non_terminal = 8
            elif non_terminal == 9:
                non_terminal = 8
            elif non_terminal == 10:
                non_terminal = 10

        elif element == 'AdU_':
            if non_terminal == 1:
                non_terminal = 1
            elif non_terminal == 2:
                non_terminal = 1
            elif non_terminal == 3:
                non_terminal = 1
            elif non_terminal == 4:
                non_terminal = 1
            elif non_terminal == 5:
                non_terminal = 1
            elif non_terminal == 6:
                non_terminal = 4
            elif non_terminal == 7:
                non_terminal = 4
            elif non_terminal == 8:
                non_terminal = 8
            elif non_terminal == 9:
                non_terminal = 8
            elif non_terminal == 10:
                non_terminal = 10

        elif element == '_AoW':
            if non_terminal == 1:
                non_terminal = 1
            elif non_terminal == 2:
                non_terminal = 2
            elif non_terminal == 3:
                non_terminal = 1
            elif non_terminal == 4:
                non_terminal = 1
            elif non_terminal == 5:
                non_terminal = 2
            elif non_terminal == 6:
                non_terminal = 4
            elif non_terminal == 7:
                non_terminal = 4
            elif non_terminal == 8:
                non_terminal = 8
            elif non_terminal == 9:
                non_terminal = 9
            elif non_terminal == 10:
                non_terminal = 10

        elif element == 'AoW_':
            if non_terminal == 1:
                non_terminal = 0
                break
            elif non_terminal == 2:
                non_terminal = 0
                break
            elif non_terminal == 3:
                non_terminal = 2
            elif non_terminal == 4:
                non_terminal = 2
            elif non_terminal == 5:
                non_terminal = 2
            elif non_terminal == 6:
                non_terminal = 5
            elif non_terminal == 7:
                non_terminal = 5
            elif non_terminal == 8:
                non_terminal = 9
            elif non_terminal == 9:
                non_terminal = 9
            elif non_terminal == 10:
                non_terminal = 10

        elif element == 'AdW_':
            if non_terminal == 1:
                non_terminal = 1
            elif non_terminal == 2:
                non_terminal = 1
            elif non_terminal == 3:
                non_terminal = 1
            elif non_terminal == 4:
                non_terminal = 1
            elif non_terminal == 5:
                non_terminal = 1
            elif non_terminal == 6:
                non_terminal = 4
            elif non_terminal == 7:
                non_terminal = 4
            elif non_terminal == 8:
                non_terminal = 8
            elif non_terminal == 9:
                non_terminal = 8
            elif non_terminal == 10:
                non_terminal = 10

        else:
            non_terminal = 0
            break

    return non_terminal


def check_ctlqx(query):
    """
    Check that `query` belongs to fragment CTLQx.

    :param query: an AST-based CTL query **in negation normal form**
    :return: True if `query` belongs to fragment CTLQx, False otherwise

    .. note:: See :func:`pytlq.utils.negation_normal_form` for the
        transformation in negation normal form.
    """
    # There must be exactly one occurrence of the placeholder in `query`.
    if count_placeholders(query) != 1:
        return False

    # A non-terminal number different from zero means that `query` belongs to
    # fragment CTLQx.
    return non_terminal_ctlqx(query) != 0
