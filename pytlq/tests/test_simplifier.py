import unittest

from pynusmv.init import init_nusmv, deinit_nusmv
from pynusmv.fsm import BddFsm

from pytlq.parser import parse_ctlq
from pytlq.checker import check_ctlqx
from pytlq.solver import solve_ctlqx
from pytlq.simplifier import project, simplify
from pytlq.utils import negation_normal_form
from pytlq.exception import VariableNotInModelError, ValueOutOfBoundsError


class TestSimplifier(unittest.TestCase):
    def setUp(self):
        init_nusmv()

    def tearDown(self):
        deinit_nusmv()

    def init_model(self, model_path):
        fsm = BddFsm.from_filename(model_path)
        self.assertIsNotNone(fsm)
        return fsm

    def test_project(self):
        ast = negation_normal_form(parse_ctlq("AG (? -> AF 'heat')"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model('examples/microwave.smv')
        projection = project(fsm, solve_ctlqx(fsm, ast), ['error'])
        self.assertEqual('(error = FALSE)', projection)

    def test_project_fail(self):
        ast = negation_normal_form(parse_ctlq("?"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model('examples/microwave.smv')
        with self.assertRaises(VariableNotInModelError):
            simplify(fsm, solve_ctlqx(fsm, ast), 1, ['a'])

    def test_simplify_candidate(self):
        ast = negation_normal_form(parse_ctlq("?"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model('examples/short.smv')
        simplification = simplify(fsm, solve_ctlqx(fsm, ast))
        self.assertEqual('(state = ready)', simplification)

    def test_simplify_conjunction(self):
        ast = negation_normal_form(parse_ctlq("AG (? -> AF 'heat')"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model('examples/microwave.smv')
        simplification = simplify(fsm, solve_ctlqx(fsm, ast), 2)
        self.assertCountEqual('(error = FALSE)\n& (close = TRUE)\n&'
                              ' ((heat = FALSE & start = TRUE) |'
                              ' (heat = TRUE & start = TRUE) |'
                              ' (heat = TRUE & start = FALSE))',
                              simplification)

    def test_simplify_all(self):
        ast = negation_normal_form(parse_ctlq("AG ?"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model('examples/microwave.smv')
        simplification = simplify(fsm, solve_ctlqx(fsm, ast))
        self.assertEqual('No possible simplification', simplification)

    def test_simplify_fail(self):
        ast = negation_normal_form(parse_ctlq("?"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model('examples/microwave.smv')
        with self.assertRaises(VariableNotInModelError):
            simplify(fsm, solve_ctlqx(fsm, ast), 1, ['a'])
        with self.assertRaises(ValueOutOfBoundsError):
            simplify(fsm, solve_ctlqx(fsm, ast), 0)
        with self.assertRaises(ValueOutOfBoundsError):
            simplify(fsm, solve_ctlqx(fsm, ast), 10)
