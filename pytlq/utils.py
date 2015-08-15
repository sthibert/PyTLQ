"""
The :mod:`pytlq.utils` module provides classes and functions used by PyTLQ
internals, and utilities for manipulating CTL formulas/queries.
"""

__all__ = ['HashableDict', 'ast_to_spec', 'bdd_to_set', 'negation_normal_form',
           'replace_placeholder', 'count_placeholders', 'path_to_placeholder']

from pynusmv.prop import (true, false, atom,
                          not_, and_, or_, imply, iff,
                          af, ag, ax, au, aw, ef, eg, ex, eu, ew)

from .ast import (Placeholder, TrueExp, FalseExp, Atom,
                  Not, And, Or, Imply, Iff,
                  AX, AF, AG, AU, AW, EX, EF, EG, EU, EW,
                  AoU, AoW, AdU, AdW, EoU, EoW, EdU, EdW)

# Store NotImplementedError message to avoid duplication.
NOT_IMPLEMENTED_MSG = 'Operator "{op}" is not implemented'


# =============================================================================
# ==== General-purpose classes/functions ======================================
# =============================================================================

class HashableDict(dict):
    """Define a hashable dictionary."""
    def __hash__(self):
        return hash(frozenset(self.items()))


def ast_to_spec(ast):
    """
    Return a PyNuSMV specification representing `ast`.

    :param ast: an AST-based CTL formula
    :return: a PyNuSMV specification representing `ast`
    :rtype: :class:`pynusmv.prop.Spec`

    :raise: a :exc:`NotImplementedError` if an operator is not implemented
    """
    if isinstance(ast, TrueExp):
        return true()

    elif isinstance(ast, FalseExp):
        return false()

    elif isinstance(ast, Atom):
        return atom(ast.value)

    elif isinstance(ast, Not):
        return not_(ast_to_spec(ast.child))

    elif isinstance(ast, And):
        return and_(ast_to_spec(ast.left), ast_to_spec(ast.right))

    elif isinstance(ast, Or):
        return or_(ast_to_spec(ast.left), ast_to_spec(ast.right))

    elif isinstance(ast, Imply):
        return imply(ast_to_spec(ast.left), ast_to_spec(ast.right))

    elif isinstance(ast, Iff):
        return iff(ast_to_spec(ast.left), ast_to_spec(ast.right))

    elif isinstance(ast, AX):
        return ax(ast_to_spec(ast.child))

    elif isinstance(ast, AF):
        return af(ast_to_spec(ast.child))

    elif isinstance(ast, AG):
        return ag(ast_to_spec(ast.child))

    elif isinstance(ast, AU):
        return au(ast_to_spec(ast.left), ast_to_spec(ast.right))

    elif isinstance(ast, AW):
        return aw(ast_to_spec(ast.left), ast_to_spec(ast.right))

    elif isinstance(ast, EX):
        return ex(ast_to_spec(ast.child))

    elif isinstance(ast, EF):
        return ef(ast_to_spec(ast.child))

    elif isinstance(ast, EG):
        return eg(ast_to_spec(ast.child))

    elif isinstance(ast, EU):
        return eu(ast_to_spec(ast.left), ast_to_spec(ast.right))

    elif isinstance(ast, EW):
        return ew(ast_to_spec(ast.left), ast_to_spec(ast.right))

    # A(phi oU psi) <=> A(phi U (phi & psi))
    elif isinstance(ast, AoU):
        return au(ast_to_spec(ast.left),
                  and_(ast_to_spec(ast.left), ast_to_spec(ast.right)))

    # A(phi oW psi) <=> A(phi W (phi & psi))
    elif isinstance(ast, AoW):
        return aw(ast_to_spec(ast.left),
                  and_(ast_to_spec(ast.left), ast_to_spec(ast.right)))

    # A(phi dU psi) <=> A(phi U (!phi & psi))
    elif isinstance(ast, AdU):
        return au(ast_to_spec(ast.left),
                  and_(not_(ast_to_spec(ast.left)), ast_to_spec(ast.right)))

    # A(phi dW psi) <=> A(phi W (!phi & psi))
    elif isinstance(ast, AdW):
        return aw(ast_to_spec(ast.left),
                  and_(not_(ast_to_spec(ast.left)), ast_to_spec(ast.right)))

    # E(phi oU psi) <=> E(phi U (phi & psi))
    elif isinstance(ast, EoU):
        return eu(ast_to_spec(ast.left),
                  and_(ast_to_spec(ast.left), ast_to_spec(ast.right)))

    # E(phi oW psi) <=> E(phi W (phi & psi))
    elif isinstance(ast, EoW):
        return ew(ast_to_spec(ast.left),
                  and_(ast_to_spec(ast.left), ast_to_spec(ast.right)))

    # E(phi dU psi) <=> E(phi U (!phi & psi))
    elif isinstance(ast, EdU):
        return eu(ast_to_spec(ast.left),
                  and_(not_(ast_to_spec(ast.left)), ast_to_spec(ast.right)))

    # E(phi dW psi) <=> E(phi W (!phi & psi))
    elif isinstance(ast, EdW):
        return ew(ast_to_spec(ast.left),
                  and_(not_(ast_to_spec(ast.left)), ast_to_spec(ast.right)))

    else:
        raise NotImplementedError(NOT_IMPLEMENTED_MSG.format(op=type(ast)))


def bdd_to_set(fsm, bdd):
    """
    Return a Set representing `bdd`.

    :param fsm: the concerned FSM
    :param bdd: a :class:`pynusmv.dd.BDD` representing a set of states
    :return: a Set representing `bdd`
    """
    return set(HashableDict(state.get_str_values()) for state
               in fsm.pick_all_states(bdd))


# =============================================================================
# ==== AST transformations ====================================================
# =============================================================================

def _double_negation(subformula):
    """Take care of the double negation in `subformula`."""
    if isinstance(subformula, Not):
        return subformula.child
    else:
        return Not(subformula)


def negation_normal_form(ast):
    """
    Transform `ast` in negation normal form.

    :param ast: an AST-based CTL formula/query
    :return: an AST-based CTL formula/query in negation normal form

    :raise: a :exc:`NotImplementedError` if an operator is not implemented
    """
    if (isinstance(ast, Placeholder) or isinstance(ast, TrueExp)
            or isinstance(ast, FalseExp) or isinstance(ast, Atom)):
        return ast

    elif (isinstance(ast, AX) or isinstance(ast, AG)
          or isinstance(ast, AF) or isinstance(ast, EX)
          or isinstance(ast, EG) or isinstance(ast, EF)):
        return type(ast)(negation_normal_form(ast.child))

    elif (isinstance(ast, And) or isinstance(ast, Or)
          or isinstance(ast, AU) or isinstance(ast, AW)
          or isinstance(ast, EU) or isinstance(ast, EW)
          or isinstance(ast, AoU) or isinstance(ast, AoW)
          or isinstance(ast, EoU) or isinstance(ast, EoW)
          or isinstance(ast, AdU) or isinstance(ast, AdW)
          or isinstance(ast, EdU) or isinstance(ast, EdW)):
        return type(ast)(negation_normal_form(ast.left),
                         negation_normal_form(ast.right))

    # phi -> psi <=> !phi | psi
    elif isinstance(ast, Imply):
        return Or(negation_normal_form(Not(ast.left)),
                  negation_normal_form(ast.right))

    # phi <-> psi <=> (!phi | psi) & (phi | !psi)
    elif isinstance(ast, Iff):
        return And(Or(negation_normal_form(Not(ast.left)),
                      negation_normal_form(ast.right)),
                   Or(negation_normal_form(ast.left),
                      negation_normal_form(Not(ast.right))))

    elif isinstance(ast, Not):
        if (isinstance(ast.child, Placeholder)
                or isinstance(ast.child, TrueExp)
                or isinstance(ast.child, FalseExp)
                or isinstance(ast.child, Atom)):
            return ast

        # !(!phi) <=> phi
        elif isinstance(ast.child, Not):
            return negation_normal_form(ast.child.child)

        elif len(ast.child) == 1:
            child = _double_negation(ast.child.child)

            # !(EX phi) <=> AX !phi
            if isinstance(ast.child, EX):
                return AX(negation_normal_form(child))

            # !(AX phi) <=> EX !phi
            elif isinstance(ast.child, AX):
                return EX(negation_normal_form(child))

            # !(EF phi) <=> AG !phi
            elif isinstance(ast.child, EF):
                return AG(negation_normal_form(child))

            # !(AF phi) <=> EG !phi
            elif isinstance(ast.child, AF):
                return EG(negation_normal_form(child))

            # !(EG phi) <=> AF !phi
            elif isinstance(ast.child, EG):
                return AF(negation_normal_form(child))

            # !(AG phi) <=> EF !phi
            elif isinstance(ast.child, AG):
                return EF(negation_normal_form(child))

            else:
                raise NotImplementedError(NOT_IMPLEMENTED_MSG
                                          .format(op=type(ast)))

        elif len(ast.child) == 2:
            left = _double_negation(ast.child.left)
            right = _double_negation(ast.child.right)

            # !(phi & psi) <=> !phi | !psi
            if isinstance(ast.child, And):
                return Or(negation_normal_form(left),
                          negation_normal_form(right))

            # !(phi | psi) <=> !phi & !psi
            elif isinstance(ast.child, Or):
                return And(negation_normal_form(left),
                           negation_normal_form(right))

            # !(phi -> psi) <=> phi & !psi
            elif isinstance(ast.child, Imply):
                return And(negation_normal_form(ast.child.left),
                           negation_normal_form(right))

            # !(phi <-> psi) <=> (phi & !psi) | (!phi & psi)
            elif isinstance(ast.child, Iff):
                return Or(And(negation_normal_form(ast.child.left),
                              negation_normal_form(right)),
                          And(negation_normal_form(left),
                              negation_normal_form(ast.child.right)))

            # !(E[phi U psi]) <=> A[!psi oW !phi]
            elif isinstance(ast.child, EU):
                return AoW(negation_normal_form(right),
                           negation_normal_form(left))

            # !(A[phi U psi]) <=> E[!psi oW !phi]
            elif isinstance(ast.child, AU):
                return EoW(negation_normal_form(right),
                           negation_normal_form(left))

            # !(E[phi W psi]) <=> A[!psi oU !phi]
            elif isinstance(ast.child, EW):
                return AoU(negation_normal_form(right),
                           negation_normal_form(left))

            # !(A[phi W psi]) <=> E[!psi oU !phi]
            elif isinstance(ast.child, AW):
                return EoU(negation_normal_form(right),
                           negation_normal_form(left))

            # !(E[phi oU psi]) <=> A[!psi W !phi]
            elif isinstance(ast.child, EoU):
                return AW(negation_normal_form(right),
                          negation_normal_form(left))

            # !(A[phi oU psi]) <=> E[!psi W !phi]
            elif isinstance(ast.child, AoU):
                return EW(negation_normal_form(right),
                          negation_normal_form(left))

            # !(E[phi oW psi]) <=> A[!psi U !phi]
            elif isinstance(ast.child, EoW):
                return AU(negation_normal_form(right),
                          negation_normal_form(left))

            # !(A[phi oW psi]) <=> E[!psi U !phi]
            elif isinstance(ast.child, AoW):
                return EU(negation_normal_form(right),
                          negation_normal_form(left))

            # !(E[phi dU psi]) <=> A[(phi | !psi) oW !phi]
            elif isinstance(ast.child, EdU):
                return AoW(Or(negation_normal_form(ast.child.left),
                              negation_normal_form(right)),
                           negation_normal_form(left))

            # !(A[phi dU psi]) <=> E[(phi | !psi) oW !phi]
            elif isinstance(ast.child, AdU):
                return EoW(Or(negation_normal_form(ast.child.left),
                              negation_normal_form(right)),
                           negation_normal_form(left))

            # !(E[phi dW psi]) <=> A[(phi | !psi) oU !phi]
            elif isinstance(ast.child, EdW):
                return AoU(Or(negation_normal_form(ast.child.left),
                              negation_normal_form(right)),
                           negation_normal_form(left))

            # !(A[phi dW psi]) <=> E[(phi | !psi) oU !phi]
            elif isinstance(ast.child, AdW):
                return EoU(Or(negation_normal_form(ast.child.left),
                              negation_normal_form(right)),
                           negation_normal_form(left))

            else:
                raise NotImplementedError(NOT_IMPLEMENTED_MSG
                                          .format(op=type(ast)))

        else:
            raise NotImplementedError(NOT_IMPLEMENTED_MSG
                                      .format(op=type(ast)))

    else:
        raise NotImplementedError(NOT_IMPLEMENTED_MSG.format(op=type(ast)))


def replace_placeholder(query, formula):
    """
    Replace all the occurrences of the placeholder of `query` with `formula`.

    :param query: an AST-based CTL query
    :param formula: an AST-based CTL formula
    :return: an AST-based CTL formula

    :raise: a :exc:`NotImplementedError` if an operator is not implemented
    """
    if len(query) == 0:
        if isinstance(query, Placeholder):
            return formula
        else:
            return query

    elif len(query) == 1:
        if isinstance(query, Atom):
            return query
        else:
            return type(query)(replace_placeholder(query.child, formula))

    elif len(query) == 2:
        return type(query)(replace_placeholder(query.left, formula),
                           replace_placeholder(query.right, formula))

    else:
        raise NotImplementedError(NOT_IMPLEMENTED_MSG.format(op=type(query)))


# =============================================================================
# ==== Placeholder operations =================================================
# =============================================================================

def count_placeholders(query, counter=0):
    """
    Count how many occurrences of the placeholder there are in `query`.

    :param query: an AST-based CTL query
    :param counter: the counter (an accumulator variable)
    :return: the number of occurrences of the placeholder in `query`

    :raise: a :exc:`NotImplementedError` if an operator is not implemented
    """
    if len(query) == 0:
        if isinstance(query, Placeholder):
            return counter+1
        else:
            return counter

    elif len(query) == 1:
        if isinstance(query, Atom):
            return counter
        else:
            return count_placeholders(query.child, counter)

    elif len(query) == 2:
        return (count_placeholders(query.left, counter)
                + count_placeholders(query.right, counter))

    else:
        raise NotImplementedError(NOT_IMPLEMENTED_MSG.format(op=type(query)))


def path_to_placeholder(query):
    """
    Compute the path from the root of `query` to the placeholder.

    :param query: an AST-based CTL query **with exactly one occurrence of the
        placeholder**
    :return: a list of strings representing the path from the root of the AST
        to the placeholder

    :raise: a :exc:`NotImplementedError` if an operator is not implemented

    .. note:: See :func:`pytlq.utils.count_placeholders` for the verification
        that `query` contains exactly one occurrence of the placeholder.
    """
    if len(query) == 0:
        if isinstance(query, Placeholder):
            return [str(type(query).__name__)]
        else:
            return None

    elif len(query) == 1:
        if isinstance(query, Atom):
            return None
        else:
            child = path_to_placeholder(query.child)
            if child:
                return [str(type(query).__name__)] + child
            else:
                return None

    elif len(query) == 2:
        left = path_to_placeholder(query.left)
        right = path_to_placeholder(query.right)
        if left:
            # The placeholder stands in the left argument of the operator.
            return ['_' + str(type(query).__name__)] + left
        elif right:
            # The placeholder stands in the right argument of the operator.
            return [str(type(query).__name__) + '_'] + right
        else:
            return None

    else:
        raise NotImplementedError(NOT_IMPLEMENTED_MSG.format(op=type(query)))
