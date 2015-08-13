import unittest

from pynusmv.init import init_nusmv, deinit_nusmv
from pynusmv.fsm import BddFsm
from pynusmv.prop import Spec

from pytlq.ast import TrueExp
from pytlq.parser import parse_ctlq
from pytlq.utils import (HashableDict, ast_to_spec, bdd_to_set,
                         negation_normal_form as negation,
                         count_placeholders as count,
                         path_to_placeholder as path,
                         replace_placeholder as replace)


class TestUtils(unittest.TestCase):
    def init_model(self):
        fsm = BddFsm.from_filename('examples/short.smv')
        self.assertIsNotNone(fsm)
        return fsm

    def test_hashabledict(self):
        hd1 = HashableDict(a=1, b='2', c=3456, abc=0.123456, x='abc')
        hd2 = HashableDict(a=2, b='2', c=3456, abc=0.123456, x='abc')

        set_ = set()
        set_.add(hd1)
        set_.add(hd2)
        set_.add(hd1)

        self.assertEqual(len(set_), 2)

    def test_ast_to_spec(self):
        queries = ["?",
                   "~?",
                   "'request' & ?",
                   "? | 'state = ready'",
                   "? -> '!request'",
                   "'state = busy' <-> ?",
                   "AX ?",
                   "AF ?",
                   "AG ?",
                   "EX ?",
                   "EF ?",
                   "EG ?",
                   "A[True U ?]",
                   "A[? W False]",
                   "E[? U True]",
                   "E[False W ?]",
                   "A[False oU ?]",
                   "A[? oW True]",
                   "A[True dU ?]",
                   "A[? dW False]",
                   "E[False oU ?]",
                   "E[? oW True]",
                   "E[True dU ?]",
                   "E[? dW False]"]

        for query in queries:
            init_nusmv()
            self.init_model()
            self.assertIsInstance(ast_to_spec(replace(parse_ctlq(query),
                                                      TrueExp())),
                                  Spec)
            deinit_nusmv()

    def test_bdd_to_set(self):
        set_ = {HashableDict({'state': 'ready', 'request': 'TRUE'}),
                HashableDict({'state': 'ready', 'request': 'FALSE'})}

        init_nusmv()
        fsm = self.init_model()
        self.assertEqual(bdd_to_set(fsm, fsm.init), set_)
        deinit_nusmv()

    def test_negation_normal_form(self):
        queries = ["~?", "~(~?)",
                   "~('a' & ?)", "~(~'a' & ~?)",
                   "~(? | 'a')", "~(~? | ~'a')",
                   "'a' -> ?", "~'a' -> ~?",
                   "~('a' -> ?)", "~(~'a' -> ~?)",
                   "? <-> 'a'", "~? <-> ~'a'",
                   "~(? <-> 'a')", "~(~? <-> ~'a')",
                   "~EX ?", "~EX ~?",
                   "~AX ?", "~AX ~?",
                   "~EF ?", "~EF ~?",
                   "~AF ?", "~AF ~?",
                   "~EG ?", "~EG ~?",
                   "~AG ?", "~AG ~?",
                   "~E['a' U ?]", "~E[~'a' U ~?]",
                   "~A['a' U ?]", "~A[~'a' U ~?]",
                   "~E[? W 'a']", "~E[~? W ~'a']",
                   "~A[? W 'a']", "~A[~? W ~'a']",
                   "~E['a' oU ?]", "~E[~'a' oU ~?]",
                   "~A['a' oU ?]", "~A[~'a' oU ~?]",
                   "~E[? oW 'a']", "~E[~? oW ~'a']",
                   "~A[? oW 'a']", "~A[~? oW ~'a']",
                   "~E['a' dU ?]", "~E[~'a' dU ~?]",
                   "~A['a' dU ?]", "~A[~'a' dU ~?]",
                   "~E[? dW 'a']", "~E[~? dW ~'a']",
                   "~A[? dW 'a']", "~A[~? dW ~'a']",
                   "? -> ~(AF 'a')",
                   "~(EG ? <-> 'a')"]
        nnfs = ["~?", "?",
                "~'a' | ~?", "'a' | ?",
                "~? & ~'a'", "? & 'a'",
                "~'a' | ?", "'a' | ~?",
                "'a' & ~?", "~'a' & ?",
                "(~? | 'a') & (? | ~'a')", "(? | ~'a') & (~? | 'a')",
                "(? & ~'a') | (~? & 'a')", "(~? & 'a') | (? & ~'a')",
                "AX ~?", "AX ?",
                "EX ~?", "EX ?",
                "AG ~?", "AG ?",
                "EG ~?", "EG ?",
                "AF ~?", "AF ?",
                "EF ~?", "EF ?",
                "A[~? oW ~'a']", "A[? oW 'a']",
                "E[~? oW ~'a']", "E[? oW 'a']",
                "A[~'a' oU ~?]", "A['a' oU ?]",
                "E[~'a' oU ~?]", "E['a' oU ?]",
                "A[~? W ~'a']", "A[? W 'a']",
                "E[~? W ~'a']", "E[? W 'a']",
                "A[~'a' U ~?]", "A['a' U ?]",
                "E[~'a' U ~?]", "E['a' U ?]",
                "A[('a' | ~?) oW ~'a']", "A[(~'a' | ?) oW 'a']",
                "E[('a' | ~?) oW ~'a']", "E[(~'a' | ?) oW 'a']",
                "A[(? | ~'a') oU ~?]", "A[(~? | 'a') oU ?]",
                "E[(? | ~'a') oU ~?]", "E[(~? | 'a') oU ?]",
                "~? | EG ~'a'",
                "(EG ? & ~'a') | (AF ~? & 'a')"]

        for (query, nnf) in zip(queries, nnfs):
            self.assertEqual(negation(parse_ctlq(query)), parse_ctlq(nnf))

    def test_replace_placeholder(self):
        query1 = "? | 'a'"
        query2 = "True -> AG ('a' & ?)"
        query3 = "A [? U AG ('b' -> False & AX ?)]"

        self.assertEqual(count(replace(parse_ctlq(query1), TrueExp())), 0)
        self.assertEqual(count(replace(parse_ctlq(query2), TrueExp())), 0)
        self.assertEqual(count(replace(parse_ctlq(query3), TrueExp())), 0)

    def test_count_placeholders(self):
        query1 = "? | 'a'"
        query2 = "? -> AG ('a' & ?)"
        query3 = "A [? U AG (? -> 'a' & AX ?)]"

        self.assertEqual(count(parse_ctlq(query1)), 1)
        self.assertEqual(count(parse_ctlq(query2)), 2)
        self.assertEqual(count(parse_ctlq(query3)), 3)

    def test_path_to_placeholder(self):
        query1 = "? | 'a'"
        query2 = "True -> AG ('a' & ?)"
        query3 = "A ['a' U AG (AX ? & 'b' -> A[False U True])]"

        self.assertEqual(path(parse_ctlq(query1)),
                         ['_Or', 'Placeholder'])
        self.assertEqual(path(parse_ctlq(query2)),
                         ['Imply_', 'AG', 'And_', 'Placeholder'])
        self.assertEqual(path(parse_ctlq(query3)),
                         ['AU_', 'AG', '_Imply', '_And', 'AX', 'Placeholder'])
