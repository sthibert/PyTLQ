"""
The :mod:`pytlq.pytlq` module provides the command-line interface to run PyTLQ
as a standalone script.
"""

import sys
import click
from pprint import pprint

from pynusmv.init import init_nusmv
from pynusmv.glob import load, compute_model, prop_database
from pynusmv.dd import enable_dynamic_reordering

from pytlq.parser import parse_ctlq
from pytlq.checker import check_ctlqx
from pytlq.solver import solve_ctlqx
from pytlq.simplifier import project, simplify
from pytlq.utils import negation_normal_form, bdd_to_set


# =============================================================================
# ==== Command-line interface =================================================
# =============================================================================

@click.command()
@click.version_option()
@click.argument('model_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('query', type=str)
@click.option('--order', type=click.Path(exists=True, dir_okay=False),
              help='Path of the order (.ord) file.')
def cli(model_path, query, order):
    """Solve QUERY that belongs to fragment CTLQx for model in MODEL_PATH."""
    try:
        # Parse `query` and transform it in NNF.
        ast = negation_normal_form(parse_ctlq(query))

        # Check that `query` belongs to fragment CTLQx.
        if not check_ctlqx(ast):
            click.echo('Error: {query} does not belong to CTLQx'
                       .format(query=query))
            # Quit PyTLQ.
            sys.exit()

        # Initialize NuSMV.
        with init_nusmv():
            # Load model from `model_path`.
            load(model_path)
            # Enable dynamic reordering of the variables.
            enable_dynamic_reordering()
            # Check if an order file is given.
            if order:
                # Build model with pre-calculated variable ordering.
                compute_model(variables_ordering=order)
            else:
                # Build model.
                compute_model()
            # Retrieve FSM of the model.
            fsm = prop_database().master.bddFsm

            # Solve `query` in `fsm`.
            solution = solve_ctlqx(fsm, ast)

            # Display solution.
            click.echo('Solution states:')
            if not solution:
                click.echo('No solution')
                # Quit PyTLQ.
                sys.exit()
            elif solution.is_false():
                click.echo('False')
                # Quit PyTLQ.
                sys.exit()
            else:
                size = fsm.count_states(solution)
                if size > 100:
                    if click.confirm('The number of states is too large'
                                     ' ({size}). Do you still want to print'
                                     ' them?'.format(size=size)):
                        pprint(bdd_to_set(fsm, solution))
                else:
                    pprint(bdd_to_set(fsm, solution))

            # Ask for further manipulations.
            while True:
                command = click.prompt('\nWhat do you want to do?'
                                       '\n  1. Project the solution on a'
                                       ' subset of the variables'
                                       '\n  2. Simplify the solution according'
                                       ' to Chan\'s approximate conjunctive'
                                       ' decomposition'
                                       '\n  3. Quit PyTLQ'
                                       '\nYour choice',
                                       type=click.IntRange(1, 3), default=3)

                # Check if solution must be projected or simplified.
                if command == 1 or command == 2:

                    # Gather more information.
                    click.echo('')
                    if command == 2:
                        maximum = click.prompt('Please enter the maximum'
                                               ' number of variables that must'
                                               ' appear in the conjuncts of'
                                               ' the simplification', type=int,
                                               default=1)
                    variables = click.prompt('Please enter the list of'
                                             ' variables of interest,'
                                             ' separated by commas', type=str,
                                             default='all the variables')
                    # Format `variables`.
                    if variables == 'all the variables':
                        variables = None
                    else:
                        variables = variables.replace(" ", "").split(',')

                    if command == 1:
                        # Project solution and display projection.
                        click.echo('\nProjection:')
                        click.echo(project(fsm, solution, variables))
                    else:
                        # Simplify solution and display simplification.
                        click.echo('\nApproximate conjunctive decomposition:')
                        click.echo(simplify(fsm, solution, maximum, variables))

                # No further manipulations are needed.
                else:
                    break

    except Exception as error:
        click.echo('Error: {msg}'.format(msg=error))
