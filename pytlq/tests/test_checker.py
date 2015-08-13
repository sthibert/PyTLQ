import unittest

from pytlq.parser import parse_ctlq
from pytlq.checker import check_ctlqx
from pytlq.utils import negation_normal_form


class TestChecker(unittest.TestCase):
    def test_ok(self):
        oks = ["?", "~?", "? & 'a'", "'a' & ?", "? | 'a'", "'a' | ?",
               "? -> 'a'", "'a' -> ?", "AX ?", "AG ?", "~EX ?", "~EF ?",
               "A[? U 'a']", "A[? W 'a']", "A[? oU 'a']", "A[? oW 'a']",
               "A['a' dW ?]", "A['a' dU ?]", "AX ((AG A['b' dU ?]) | EX 'a')",
               "~(? -> AF 'a')", "True & A[? U 'a']", "True | A[? U 'a']",
               "True & A['a' oU A[? U 'b']]", "True | A['a' oU A[? U 'b']]",
               "AX A[? U 'a']", "AX A['a' oU A[? U 'b']]", "AF A[? U 'a']",
               "AG A[? U 'a']", "AG A['a' oU A[? U 'b']]",
               "A[A[? U 'a'] U 'b']", "A[A['a' oU A[? U 'b']] U 'c']",
               "A['a' U A[? U 'b']]", "A[A[? U 'a'] W 'b']",
               "A[A['a' oU A[? U 'b']] W 'c']", "A['a' W A[? U 'b']]",
               "A[A[? U 'a'] oU 'b']", "A[A['a' oU A[? U 'b']] oU 'c']",
               "A['a' dU A[? U 'b']]", "A['a' dU A['b' oU A[? U 'c']]]",
               "A[A[? oW 'a'] U 'b']", "A[A[? U 'a'] oW 'b']",
               "A[A['a' oU A[? U 'b']] oW 'c']", "A['a' oW A[? U 'b']]",
               "A['a' dW A[? U 'b']]", "A['a' dW A['b' oU A[? U 'c']]]",
               "A['a' W A['b' W A[? U 'c']]]", "A[A[A[? U 'a'] W 'b'] W 'c']",
               "A['a' U A['b' W A[? U 'c']]]", "A[A[A[? U 'a'] W 'b'] U 'c']",
               "AG A['b' W A[? U 'c']]", "AF A['b' W A[? U 'c']]",
               "A['a' dW A['b' W A['c' U AG AG ?]]]", "AF A['a' oW AG ?]",
               "A['a' oU A[AG ? oU 'b']]", "A['a' oW A[AG ? oW 'b']]",
               "A['a' dU A['b' dU A['c' oW AG ?]]]", "AX A['a' oW AG ?]",
               "AF A['a' oW ('b' | A['c' oW AG ?])]", "AF A[AG ? U False]",
               "A['a' dW A['b' oW A[A[A['c' oW AG ?] oU 'd'] oW 'e']]]",
               "A['a' U A['b' oW AG ?]]", "A['a' W A['b' oW AG ?]]",
               "A['a' oU A['b' oW AG ?]]", "AG A['a' oU A[AG ? U 'b']]",
               "AG AX AF ('a' | ('b' & AG A['c' oW AG ?]))",
               "A['a' W A[A['b' U A[AG A['c' oW AG ?] U 'd']] W 'e']]",
               "A['a' oW A[A['b' oU A[AG A['c' oW AG ?] oU 'd']] oW 'e']]",
               "A['a' dU A['b' dW AG A['c' oW AG ?]]]",
               "A['a' dU (AG A['b' dW ('c' | AG ?)] | 'd')]",
               "A[('a' | AG A['b' oU (AG ? | 'c')]) oU 'd']",
               "A[('a' | AG A['b' U (AG ? | 'c')]) U 'd']",
               "A[('a' | AG A['b' W (AG ? | 'c')]) W 'd']",
               "A['a' W A['b' oU A[A['c' oW AG ?] U 'd']]]",
               "A[A['a' oW A[A['b' oW AG ?] W 'c']] U 'd']",
               "A[A['a' oU A[AG ? U 'b']] W 'c']",
               "A['a' U A['b' oU A[AG ? U 'c']]]"]

        for ok in oks:
            self.assertTrue(check_ctlqx(negation_normal_form(parse_ctlq(ok))))

    def test_ko(self):
        kos = ["? <-> 'a'", "'a' <-> ?", "AF ?", "A['a' U ?]", "A['a' W ?]",
               "A['a' oU ?]", "A['a' oW ?]", "A[? dU 'a']", "A[? dW 'a']",
               "EX ?", "EF ?", "EG ?", "~AX ?", "~AF ?", "~AG ?", "E['a' U ?]",
               "E[? U 'a']", "E['a' W ?]", "E[? W 'a']", "E['a' oU ?]",
               "E[? oU 'a']", "E['a' oW ?]", "E[? oW 'a']", "E['a' dU ?]",
               "E[? dU 'a']", "E['a' dW ?]", "E[? dW 'a']", "~('a' -> AF ?)",
               "AF ('a' & AF ('b' | AG ?))", "AX ((AF A[? dU 'b']) | 'a')",
               "AF A[True oU A[? U 'a']]", "A['a' U A[True oU A[? U 'b']]]",
               "A['a' W A[True oU A[? U 'b']]]",
               "A['a' oU A[True oU A[? U 'b']]]",
               "A['a' oW A[True oU A[? U 'b']]]",
               "AF AX (A['a' W A[? U 'b']] | False)",
               "AF A['a' dW A['b' W A[? U 'c']]]",
               "AF A['a' oW A['b' W A[? U 'c']]]",
               "AF A[A['a' W A[? U 'b']] oW 'c']",
               "AF A['a' dU A['b' W A[? U 'c']]]",
               "AF A['a' oU A['b' W A[? U 'c']]]",
               "AF A[A['a' W A[? U 'b']] oU 'c']",
               "AF AX A[AF AX (AG ? & True) U False]",
               "A['a' U A['b' oU A[A[A['c' dW AG ?] W 'e'] oW 'f']]]",
               "AF AX ('a' & (('b' & A['c' oW AG ?]) | 'd'))",
               "AF AX ('a' & (('b' & ('c' | A['d' oW AG ?])) | 'e'))",
               "AF ('a' & A['b' oW (A['c' oW AG ?] | 'd')])",
               "AF AX A['b' oW (A['c' oW AG ?] | 'd')]",
               "AF AX (('a' | A[AG ? U 'b']) & 'c')",
               "AF ('a' & (A['b' oW (A['c' oW AG ?] | 'd')] | 'e'))",
               "A['a' U A['b' dW A['c' oU A[AG (AG ? | 'd') U 'e']]]]",
               "A['a' U A['b' oU A['c' oU A[AG (AG ? | 'd') U 'e']]]]",
               "A['a' U A[A['b' oU A[AG (AG ? | 'c') U 'd']] oU 'e']]",
               "A['a' U A['b' dU A['c' oU A[AG (AG ? | 'd') U 'e']]]]",
               "A['a' U A[A['b' oU A[AG (AG ? | 'c') U 'd']] oW 'e']]",
               "A['a' U A['b' oW A['c' oU A[AG (AG ? | 'd') U 'e']]]]",
               "AF A['a' oU A['b' oW A[AG A[AG ? U 'c'] U 'd']]]",
               "A['a' U AX A['b' U A[AG ? U 'c']]]",
               "A['a' U AX A['b' W A[AG ? U 'c']]]",
               "A['a' U AX A['b' dU A[AG ? U 'c']]]",
               "A['a' U AX A['b' dW A[AG ? U 'c']]]",
               "A['a' U AX A[A[AG ? U 'b'] U 'c']]",
               "A['a' U AX A[A[AG ? U 'b'] W 'c']]",
               "A['a' U AX A[A[AG ? U 'b'] oU 'c']]",
               "A['a' U AX A[A[AG ? U 'b'] oW 'c']]"]

        for ko in kos:
            self.assertFalse(check_ctlqx(negation_normal_form(parse_ctlq(ko))))

    def test_ko_not_nnf(self):
        kos = ["~AX ?", "~EX ?", "~EF ?", "? -> 'a'", "'a' -> ?",
               "~(? -> AF 'a')"]

        for ko in kos:
            self.assertFalse(check_ctlqx(parse_ctlq(ko)))
