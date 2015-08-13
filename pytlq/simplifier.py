"""
The :mod:`pytlq.simplifier` module provides functions to simplify the solutions
returned by the solver.
"""

__all__ = ['project', 'simplify']

import itertools

from pynusmv.dd import BDD

from .utils import HashableDict
from .exception import ValueOutOfBoundsError, VariableNotInModelError


def _pre_process_variables(variables, all_variables):
    """Perform pre-processing of `variables`."""
    if variables is None:
        return all_variables
    else:
        # Check that the given variables are present in the model.
        for variable in variables:
            if variable not in all_variables:
                raise VariableNotInModelError('Variable "{var}" is not present'
                                              ' in the model'
                                              .format(var=variable))
        return variables


def _projection_to_string(projection):
    """
    Transform the projection of the solution, which has the form of a Set of
    HashableDicts, in a clear and understandable String.
    """
    return ' | '.join(
        '({0})'.format(
            ' & '.join(
                '{0} = {1}'.format(variable, value)
                for variable, value in dict_.items()
            )
        )
        for dict_ in projection
    )


def _simplification_to_string(simplification):
    """
    Transform the simplification of the solution, which has the form of a List
    of Strings, in a clear and understandable String.
    """
    if simplification:
        return '\n& '.join(
            ('({0})' if str_.count('(') > 1 else '{0}').format(str_)
            for str_ in simplification
        )

    else:
        return 'No possible simplification'


def project(fsm, states, variables=None):
    """
    Project `states` on `variables` (in other words, enumerate all the possible
    values of the variables in `variables`, in all states of `states`).

    :param fsm: the concerned FSM
    :param states: a set of states
    :param variables: the list of variables on which `states` is projected (by
        default: all the variables)
    :return: a String representing the projection of `states` on the variables
        of `variables`

    :raise: a :exc:`pytlq.exception.VariableNotInModelError` if a variable of
        `variables` is not present in the model
    """
    all_variables = fsm.bddEnc.stateVars
    # Pre-process `variables`.
    variables = _pre_process_variables(variables, all_variables)
    # Compute the complement List of variables.
    complement = list(variable for variable in all_variables
                      if variable not in variables)
    # Initialize the output Set.
    result = set()

    # Apply states mask.
    states = states & fsm.bddEnc.statesMask

    while states.isnot_false():
        # Select one state in `states`.
        state = fsm.pick_one_state(states)
        # Get the value of the variables of `variables` from `state`.
        result.add(HashableDict({variable: value for variable, value
                                 in state.get_str_values().items()
                                 if variable in variables}))

        # Remove the states in which the value of variables are the same as
        # the one we just added in `result` (in order to avoid dealing with
        # the same information twice).
        states -= state.forsome(fsm.bddEnc.cube_for_state_vars(complement))

    return _projection_to_string(result)


def simplify(fsm, states, maximum=1, variables=None):
    """
    Compute the approximate conjunctive decomposition of `states`.

    :param fsm: the concerned FSM
    :param states: a set of states
    :param maximum: the maximum number of variables that must appear in the
        conjuncts of the approximate conjunctive decomposition (by default: 1)
    :param variables: the list of variables to which the solution is restricted
        (by default: all the variables)
    :return: a String representing the approximate conjunctive decomposition
        of `states`, if a simplification is possible

    :raise: a :exc:`pytlq.exception.ValueOutOfBoundsError` if `maximum` is not
        in the correct bounds
    :raise: a :exc:`pytlq.exception.VariableNotInModelError` if a variable of
        `variables` is not present in the model

    .. note:: This function is adapted from Chan's approximate conjunctive
        decomposition of a propositional formula, defined at CAV 2000.
    """
    all_variables = fsm.bddEnc.stateVars
    # Pre-process `variables`.
    variables = _pre_process_variables(variables, all_variables)
    # Check that `maximum` is in the correct bounds.
    if maximum < 1 or maximum > len(variables):
        raise ValueOutOfBoundsError('Value "{val}" is out of bounds, input'
                                    ' must be in range 1..{n}'
                                    .format(val=maximum, n=len(variables)))

    # Initialize the output List.
    result = []
    # The empty conjunction is represented by the BDD True.
    conjunction = BDD.true(fsm.bddEnc.DDmanager)

    for size in range(1, maximum+1):
        for variables_subsequence in itertools.combinations(variables, size):
            # Compute the complement List of variables.
            complement = list(variable for variable in all_variables
                              if variable not in variables_subsequence)

            # Existentially abstract all the variables in `complement` from
            # `states`.
            candidate = states.forsome(
                fsm.bddEnc.cube_for_state_vars(complement)
            )
            # Restrict `candidate` with `conjunction`.
            candidate = candidate.minimize(conjunction)

            # Check if `candidate` can represent the solution on its own.
            if candidate == states:
                result.append(project(fsm, candidate, variables_subsequence))
                return _simplification_to_string(result)

            # Check if `candidate` adds useful information.
            elif candidate.isnot_true():
                result.append(project(fsm, candidate, variables_subsequence))
                conjunction = conjunction & candidate

                # Check if `conjunction` can represent the solution on its own.
                if conjunction == states:
                    return _simplification_to_string(result)

    return _simplification_to_string(result)
