"""
The :mod:`pytlq.solver` module provides functions to solve CTL queries that
belong to fragment CTLQx.
"""

__all__ = ['solve_ctlqx']

from pynusmv.dd import BDD
from pynusmv.mc import eval_ctl_spec
from pynusmv.utils import fixpoint

from .ast import (Placeholder, TrueExp, FalseExp, Not, And, Or, AX, AF, AG, AU,
                  AW, AoU, AoW, AdU, AdW)
from .utils import ast_to_spec, count_placeholders, replace_placeholder


def _reachable(fsm, phi, states):
    """
    First auxiliary set, as defined by Chan at CAV 2000.

    :param fsm: the concerned FSM
    :param phi: an AST-based CTL formula
    :param states: a set of states
    :return: the states of `fsm` that are reachable from states in `states` by
        going only through states at which `phi` holds
    :rtype: :class:`pynusmv.dd.BDD`
    """
    return fixpoint(lambda z: ((states | fsm.post(z))
                               & eval_ctl_spec(fsm, ast_to_spec(phi))),
                    BDD.false(fsm.bddEnc.DDmanager))  # Least fixed point.


def _cycle(fsm, gamma, phi, states):
    """
    Second auxiliary set, as defined by Chan at CAV 2000.

    :param fsm: the concerned FSM
    :param gamma: an AST-based CTL query
    :param phi: an AST-based CTL formula
    :param states: a set of states
    :return: all states within a cycle in the first auxiliary set
    :rtype: :class:`pynusmv.dd.BDD`
    """
    psi = replace_placeholder(gamma, FalseExp())
    new_phi = And(phi, Not(psi))
    return fixpoint(lambda z: _reachable(fsm, new_phi, states) & fsm.post(z),
                    BDD.true(fsm.bddEnc.DDmanager))  # Greatest fixed point.


def _boundary(fsm, gamma, phi, states):
    """
    Third auxiliary set, as defined by Chan at CAV 2000.

    :param fsm: the concerned FSM
    :param gamma: an AST-based CTL query
    :param phi: an AST-based CTL formula
    :param states: a set of states
    :return: the boundary of the first auxiliary set (that is, the first states
        on each path starting from `states` that are not in the first auxiliary
        set and at which `gamma[False]` does not hold)
    :rtype: :class:`pynusmv.dd.BDD`
    """
    psi = replace_placeholder(gamma, FalseExp())
    new_phi = And(phi, Not(psi))
    return ((states | fsm.post(_reachable(fsm, new_phi, states)))
            - (eval_ctl_spec(fsm, ast_to_spec(phi))
               | eval_ctl_spec(fsm, ast_to_spec(psi))))


def _f_sol(fsm, gamma, phi, states, cycle):
    """
    Find the states of `fsm` with highest indices among the states at which
    `gamma` has a solution, as defined by Samer and Veith at TIME'05.

    :param fsm: the concerned FSM
    :param gamma: an AST-based CTL query
    :param phi: an AST-based CTL formula
    :param states: a set of states
    :param cycle: True if there is a cycle, False otherwise
    :return: the states of `fsm` with highest indices among the states at which
        `gamma` has a solution
    :rtype: :class:`pynusmv.dd.BDD`
    """
    if cycle:
        c = _cycle(fsm, gamma, phi, states)
    else:
        c = BDD.false(fsm.bddEnc.DDmanager)

    chi = replace_placeholder(gamma, TrueExp())
    psi = replace_placeholder(gamma, FalseExp())
    new_phi = And(phi, Not(psi))

    u_1 = fixpoint(lambda z: ((c - eval_ctl_spec(fsm, ast_to_spec(chi)))
                              & fsm.post(z)),
                   BDD.true(fsm.bddEnc.DDmanager))  # Greatest fixed point.

    u_2 = u_1 | (_boundary(fsm, gamma, phi, states)
                 - eval_ctl_spec(fsm, ast_to_spec(chi)))

    u_3 = fixpoint(lambda z: (((u_2 | fsm.pre(z))
                               & _reachable(fsm, new_phi, states))
                              - eval_ctl_spec(fsm, ast_to_spec(chi))),
                   BDD.false(fsm.bddEnc.DDmanager))  # Least fixed point.

    return (((fsm.pre(u_3) & _reachable(fsm, new_phi, states))
             | _boundary(fsm, gamma, phi, states) | c)
            & eval_ctl_spec(fsm, ast_to_spec(chi)))


def _e_sol(fsm, gamma, states):
    """
    Compute the unique set of solution states of `fsm` to `gamma` at `states`,
    as defined by Samer and Veith at TIME'05.

    :param fsm: the concerned FSM
    :param gamma: an AST-based CTL query that belongs to fragment CTLQx
    :param states: a set of states
    :return: the unique set of solution states of `fsm` to `gamma` at `states`
    :rtype: :class:`pynusmv.dd.BDD`

    .. note:: Samer and Veith's algorithm has been extended to support the
        negation in front of the placeholder.
    """
    if isinstance(gamma, Placeholder):
        return states

    # Extension to support the negation in front of the placeholder.
    elif isinstance(gamma, Not) and isinstance(gamma.child, Placeholder):
        return fsm.reachable_states - states

    elif isinstance(gamma, And):
        if count_placeholders(gamma.left):
            return _e_sol(fsm, gamma.left, states)
        elif count_placeholders(gamma.right):
            return _e_sol(fsm, gamma.right, states)

    elif isinstance(gamma, Or):
        if count_placeholders(gamma.left):
            return _e_sol(fsm, gamma.left, states
                          - eval_ctl_spec(fsm, ast_to_spec(gamma.right)))
        elif count_placeholders(gamma.right):
            return _e_sol(fsm, gamma.right, states
                          - eval_ctl_spec(fsm, ast_to_spec(gamma.left)))

    elif isinstance(gamma, AX):
        return _e_sol(fsm, gamma.child, fsm.post(states))

    elif isinstance(gamma, AF):
        return _e_sol(fsm, AU(TrueExp(), gamma.child), states)

    elif isinstance(gamma, AG):
        return _e_sol(fsm, AoW(gamma.child, FalseExp()), states)

    elif isinstance(gamma, AU):
        if count_placeholders(gamma.left):
            return _e_sol(fsm, AoW(Or(gamma.right, gamma.left), gamma.right),
                          states)
        elif count_placeholders(gamma.right):
            return _e_sol(fsm, gamma.right,
                          _f_sol(fsm, gamma.right, gamma.left, states, True))

    elif isinstance(gamma, AoU):
        if count_placeholders(gamma.left):
            return _e_sol(fsm, AoW(gamma.left, gamma.right), states)
        elif count_placeholders(gamma.right):
            return _e_sol(fsm, AU(gamma.left, And(gamma.left, gamma.right)),
                          states)

    elif isinstance(gamma, AdU):
        return _e_sol(fsm, AdW(gamma.left, gamma.right), states)

    elif isinstance(gamma, AW):
        if count_placeholders(gamma.left):
            return _e_sol(fsm, AoW(Or(gamma.right, gamma.left), gamma.right),
                          states)
        elif count_placeholders(gamma.right):
            return _e_sol(fsm, gamma.right,
                          _f_sol(fsm, gamma.right, gamma.left, states, False))

    elif isinstance(gamma, AoW):
        if count_placeholders(gamma.left):
            return _e_sol(fsm, gamma.left, states
                          | fsm.post(_reachable(fsm, Not(gamma.right),
                                                states)))
        elif count_placeholders(gamma.right):
            return _e_sol(fsm, AW(gamma.left, And(gamma.left, gamma.right)),
                          states)

    elif isinstance(gamma, AdW):
        return _e_sol(fsm, gamma.right,
                      ((states | fsm.post(_reachable(fsm, gamma.left, states)))
                       - eval_ctl_spec(fsm, ast_to_spec(gamma.left))))


def solve_ctlqx(fsm, query):
    """
    Compute the unique set of solution states of `fsm` to `query` at the
    initial states of `fsm`, as defined by Samer and Veith at TIME'05.

    :param fsm: the concerned FSM
    :param query: an AST-based CTL query **that belongs to fragment CTLQx**
    :return: the unique set of solution states of `fsm` to `query` at the
        initial states of `fsm` if there is a solution, None otherwise
    :rtype: :class:`pynusmv.dd.BDD`

    .. note:: The characteristic function of the output is an exact solution to
        `query` in `fsm`.
    .. note:: See :func:`pytlq.checker.check_ctlqx` for the verification that
        `query` belongs to fragment CTLQx.
    """
    if (eval_ctl_spec(fsm, ast_to_spec(replace_placeholder(query, TrueExp())))
            .is_true()):
        return _e_sol(fsm, query, fsm.init)

    else:
        return None
