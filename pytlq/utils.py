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
    """Take care of the double negation in subformula."""
    if isinstance(subformula, Not):
        return subformula.child
    else:
        return Not(subformula)


def negation_normal_form(query):
    """
    Transform `query` in negation normal form.

    :param query: an AST-based CTL query
    :return: an AST-based CTL query in negation normal form

    :raise: a :exc:`NotImplementedError` if an operator is not implemented
    """
    if (isinstance(query, Placeholder) or isinstance(query, TrueExp)
            or isinstance(query, FalseExp) or isinstance(query, Atom)):
        return query

    elif (isinstance(query, AX) or isinstance(query, AG)
          or isinstance(query, AF) or isinstance(query, EX)
          or isinstance(query, EG) or isinstance(query, EF)):
        return type(query)(negation_normal_form(query.child))

    elif (isinstance(query, And) or isinstance(query, Or)
          or isinstance(query, AU) or isinstance(query, AW)
          or isinstance(query, EU) or isinstance(query, EW)
          or isinstance(query, AoU) or isinstance(query, AoW)
          or isinstance(query, EoU) or isinstance(query, EoW)
          or isinstance(query, AdU) or isinstance(query, AdW)
          or isinstance(query, EdU) or isinstance(query, EdW)):
        return type(query)(negation_normal_form(query.left),
                           negation_normal_form(query.right))

    # phi -> psi <=> !phi | psi
    elif isinstance(query, Imply):
        return Or(negation_normal_form(Not(query.left)),
                  negation_normal_form(query.right))

    # phi <-> psi <=> (!phi | psi) & (phi | !psi)
    elif isinstance(query, Iff):
        return And(Or(negation_normal_form(Not(query.left)),
                      negation_normal_form(query.right)),
                   Or(negation_normal_form(query.left),
                      negation_normal_form(Not(query.right))))

    elif isinstance(query, Not):
        if (isinstance(query.child, Placeholder)
                or isinstance(query.child, TrueExp)
                or isinstance(query.child, FalseExp)
                or isinstance(query.child, Atom)):
            return query

        # !(!phi) <=> phi
        elif isinstance(query.child, Not):
            return negation_normal_form(query.child.child)

        elif len(query.child) == 1:
            child = _double_negation(query.child.child)

            # !(EX phi) <=> AX !phi
            if isinstance(query.child, EX):
                return AX(negation_normal_form(child))

            # !(AX phi) <=> EX !phi
            elif isinstance(query.child, AX):
                return EX(negation_normal_form(child))

            # !(EF phi) <=> AG !phi
            elif isinstance(query.child, EF):
                return AG(negation_normal_form(child))

            # !(AF phi) <=> EG !phi
            elif isinstance(query.child, AF):
                return EG(negation_normal_form(child))

            # !(EG phi) <=> AF !phi
            elif isinstance(query.child, EG):
                return AF(negation_normal_form(child))

            # !(AG phi) <=> EF !phi
            elif isinstance(query.child, AG):
                return EF(negation_normal_form(child))

            else:
                raise NotImplementedError(NOT_IMPLEMENTED_MSG
                                          .format(op=type(query)))

        elif len(query.child) == 2:
            left = _double_negation(query.child.left)
            right = _double_negation(query.child.right)

            # !(phi & psi) <=> !phi | !psi
            if isinstance(query.child, And):
                return Or(negation_normal_form(left),
                          negation_normal_form(right))

            # !(phi | psi) <=> !phi & !psi
            elif isinstance(query.child, Or):
                return And(negation_normal_form(left),
                           negation_normal_form(right))

            # !(phi -> psi) <=> phi & !psi
            elif isinstance(query.child, Imply):
                return And(negation_normal_form(query.child.left),
                           negation_normal_form(right))

            # !(phi <-> psi) <=> (phi & !psi) | (!phi & psi)
            elif isinstance(query.child, Iff):
                return Or(And(negation_normal_form(query.child.left),
                              negation_normal_form(right)),
                          And(negation_normal_form(left),
                              negation_normal_form(query.child.right)))

            # !(E[phi U psi]) <=> A[!psi oW !phi]
            elif isinstance(query.child, EU):
                return AoW(negation_normal_form(right),
                           negation_normal_form(left))

            # !(A[phi U psi]) <=> E[!psi oW !phi]
            elif isinstance(query.child, AU):
                return EoW(negation_normal_form(right),
                           negation_normal_form(left))

            # !(E[phi W psi]) <=> A[!psi oU !phi]
            elif isinstance(query.child, EW):
                return AoU(negation_normal_form(right),
                           negation_normal_form(left))

            # !(A[phi W psi]) <=> E[!psi oU !phi]
            elif isinstance(query.child, AW):
                return EoU(negation_normal_form(right),
                           negation_normal_form(left))

            # !(E[phi oU psi]) <=> A[!psi W !phi]
            elif isinstance(query.child, EoU):
                return AW(negation_normal_form(right),
                          negation_normal_form(left))

            # !(A[phi oU psi]) <=> E[!psi W !phi]
            elif isinstance(query.child, AoU):
                return EW(negation_normal_form(right),
                          negation_normal_form(left))

            # !(E[phi oW psi]) <=> A[!psi U !phi]
            elif isinstance(query.child, EoW):
                return AU(negation_normal_form(right),
                          negation_normal_form(left))

            # !(A[phi oW psi]) <=> E[!psi U !phi]
            elif isinstance(query.child, AoW):
                return EU(negation_normal_form(right),
                          negation_normal_form(left))

            # !(E[phi dU psi]) <=> A[(phi | !psi) oW !phi]
            elif isinstance(query.child, EdU):
                return AoW(Or(negation_normal_form(query.child.left),
                              negation_normal_form(right)),
                           negation_normal_form(left))

            # !(A[phi dU psi]) <=> E[(phi | !psi) oW !phi]
            elif isinstance(query.child, AdU):
                return EoW(Or(negation_normal_form(query.child.left),
                              negation_normal_form(right)),
                           negation_normal_form(left))

            # !(E[phi dW psi]) <=> A[(phi | !psi) oU !phi]
            elif isinstance(query.child, EdW):
                return AoU(Or(negation_normal_form(query.child.left),
                              negation_normal_form(right)),
                           negation_normal_form(left))

            # !(A[phi dW psi]) <=> E[(phi | !psi) oU !phi]
            elif isinstance(query.child, AdW):
                return EoU(Or(negation_normal_form(query.child.left),
                              negation_normal_form(right)),
                           negation_normal_form(left))

            else:
                raise NotImplementedError(NOT_IMPLEMENTED_MSG
                                          .format(op=type(query)))

        else:
            raise NotImplementedError(NOT_IMPLEMENTED_MSG
                                      .format(op=type(query)))

    else:
        raise NotImplementedError(NOT_IMPLEMENTED_MSG.format(op=type(query)))


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
