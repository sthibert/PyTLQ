import unittest

from pynusmv.init import init_nusmv, deinit_nusmv
from pynusmv.dd import BDD
from pynusmv.fsm import BddFsm

from pytlq.parser import parse_ctlq
from pytlq.checker import check_ctlqx
from pytlq.solver import solve_ctlqx
from pytlq.utils import HashableDict, negation_normal_form, bdd_to_set


class TestSolver(unittest.TestCase):
    def setUp(self):
        init_nusmv()

    def tearDown(self):
        deinit_nusmv()

    def init_model(self):
        fsm = BddFsm.from_filename('examples/admin.smv')
        self.assertIsNotNone(fsm)
        return fsm

    def test_placeholder(self):
        ast = negation_normal_form(parse_ctlq("?"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model()
        self.assertEqual(solve_ctlqx(fsm, ast), fsm.init)

    def test_not_placeholder(self):
        ast = negation_normal_form(parse_ctlq("~?"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model()
        self.assertEqual(solve_ctlqx(fsm, ast),
                         fsm.reachable_states - fsm.init)

    def test_ax(self):
        ast = negation_normal_form(parse_ctlq("AX ?"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model()
        solution = {HashableDict({'admin': 'none', 'state': 'choosing'})}
        self.assertCountEqual(bdd_to_set(fsm, solve_ctlqx(fsm, ast)), solution)

    def test_ag(self):
        ast = negation_normal_form(parse_ctlq("AG ?"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model()
        self.assertEqual(solve_ctlqx(fsm, ast), fsm.reachable_states)

    def test_af_ag(self):
        ast = negation_normal_form(parse_ctlq("AF AG ?"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model()
        solution = {HashableDict({'admin': 'bob', 'state': 'waiting'}),
                    HashableDict({'admin': 'bob', 'state': 'processing'}),
                    HashableDict({'admin': 'alice', 'state': 'waiting'}),
                    HashableDict({'admin': 'alice', 'state': 'processing'})}
        self.assertCountEqual(bdd_to_set(fsm, solve_ctlqx(fsm, ast)), solution)

    def test_ag_af(self):
        ast = negation_normal_form(parse_ctlq("AG (? -> AF 'admin = alice')"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model()
        solution = {HashableDict({'admin': 'alice', 'state': 'waiting'}),
                    HashableDict({'admin': 'alice', 'state': 'processing'})}
        self.assertCountEqual(bdd_to_set(fsm, solve_ctlqx(fsm, ast)), solution)

    def test_and(self):
        ast = negation_normal_form(parse_ctlq("AX AG (? & False)"))
        ast2 = negation_normal_form(parse_ctlq("AX AG ?"))
        self.assertTrue(check_ctlqx(ast))
        self.assertTrue(check_ctlqx(ast2))
        fsm = self.init_model()
        self.assertEqual(solve_ctlqx(fsm, ast), solve_ctlqx(fsm, ast2))

    def test_or(self):
        ast = negation_normal_form(parse_ctlq("AF ('admin = bob' | AG ?)"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model()
        solution = {HashableDict({'admin': 'alice', 'state': 'waiting'}),
                    HashableDict({'admin': 'alice', 'state': 'processing'})}
        self.assertCountEqual(bdd_to_set(fsm, solve_ctlqx(fsm, ast)), solution)

    def test_au(self):
        ast = negation_normal_form(parse_ctlq("A[? U 'state = processing']"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model()
        solution = {HashableDict({'admin': 'none', 'state': 'starting'}),
                    HashableDict({'admin': 'none', 'state': 'choosing'}),
                    HashableDict({'admin': 'alice', 'state': 'waiting'}),
                    HashableDict({'admin': 'bob', 'state': 'waiting'})}
        self.assertCountEqual(bdd_to_set(fsm, solve_ctlqx(fsm, ast)), solution)

    def test_aou(self):
        ast = negation_normal_form(parse_ctlq("A[? oU 'state = processing']"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model()
        self.assertEqual(solve_ctlqx(fsm, ast), fsm.reachable_states)

    def test_adu(self):
        ast = negation_normal_form(parse_ctlq("A['state = starting' dU ?]"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model()
        solution = {HashableDict({'admin': 'none', 'state': 'choosing'})}
        self.assertCountEqual(bdd_to_set(fsm, solve_ctlqx(fsm, ast)), solution)

    def test_aw(self):
        ast = negation_normal_form(parse_ctlq("A[? W AG 'admin = bob']"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model()
        solution = {HashableDict({'admin': 'none', 'state': 'starting'}),
                    HashableDict({'admin': 'none', 'state': 'choosing'}),
                    HashableDict({'admin': 'alice', 'state': 'waiting'}),
                    HashableDict({'admin': 'alice', 'state': 'processing'})}
        self.assertCountEqual(bdd_to_set(fsm, solve_ctlqx(fsm, ast)), solution)

    def test_aow(self):
        ast = negation_normal_form(parse_ctlq("A[? oW 'state = processing']"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model()
        self.assertEqual(solve_ctlqx(fsm, ast), fsm.reachable_states)

    def test_adw(self):
        ast = negation_normal_form(parse_ctlq("A['state = starting' dW ?]"))
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model()
        solution = {HashableDict({'admin': 'none', 'state': 'choosing'})}
        self.assertCountEqual(bdd_to_set(fsm, solve_ctlqx(fsm, ast)), solution)

    def test_false(self):
        ast = negation_normal_form(
            parse_ctlq("A['admin = bob' oW A['admin = alice' oU AG ?]]")
        )
        self.assertTrue(check_ctlqx(ast))
        fsm = self.init_model()
        self.assertEqual(solve_ctlqx(fsm, ast),
                         BDD.false(fsm.bddEnc.DDmanager))
