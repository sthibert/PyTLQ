import unittest

import pyparsing

from pytlq.ast import (AST, Placeholder, TrueExp, FalseExp,
                       Atom, Not, And, Or, Imply, Iff,
                       AX, AF, AG, AU, AW, EX, EF, EG, EU, EW,
                       AoU, AoW, AdU, AdW, EoU, EoW, EdU, EdW)
from pytlq.parser import parse_ctlq
from pytlq.exception import NoPlaceholderError


class TestParser(unittest.TestCase):
    def test_subclassing(self):
        self.assertTrue(issubclass(Placeholder, AST))
        self.assertTrue(issubclass(TrueExp, AST))
        self.assertTrue(issubclass(FalseExp, AST))
        self.assertTrue(issubclass(Atom, AST))
        self.assertTrue(issubclass(Not, AST))
        self.assertTrue(issubclass(And, AST))
        self.assertTrue(issubclass(Or, AST))
        self.assertTrue(issubclass(Imply, AST))
        self.assertTrue(issubclass(Iff, AST))
        self.assertTrue(issubclass(AX, AST))
        self.assertTrue(issubclass(AF, AST))
        self.assertTrue(issubclass(AG, AST))
        self.assertTrue(issubclass(AU, AST))
        self.assertTrue(issubclass(AW, AST))
        self.assertTrue(issubclass(EX, AST))
        self.assertTrue(issubclass(EF, AST))
        self.assertTrue(issubclass(EG, AST))
        self.assertTrue(issubclass(EU, AST))
        self.assertTrue(issubclass(EW, AST))
        self.assertTrue(issubclass(AoU, AST))
        self.assertTrue(issubclass(AoW, AST))
        self.assertTrue(issubclass(AdU, AST))
        self.assertTrue(issubclass(AdW, AST))
        self.assertTrue(issubclass(EoU, AST))
        self.assertTrue(issubclass(EoW, AST))
        self.assertTrue(issubclass(EdU, AST))
        self.assertTrue(issubclass(EdW, AST))

    def test_str(self):
        logical = parse_ctlq("~? & True | False -> 'a' <-> 'b'")
        unary = parse_ctlq("AX EX AG EG AF EF ?")
        binary = parse_ctlq("A[True U A[True W E[True U E[True W ?]]]]")
        binary2 = parse_ctlq("A[True oU A[True oW E[True oU E[True oW ?]]]]")
        binary3 = parse_ctlq("A[True dU A[True dW E[True dU E[True dW ?]]]]")

        self.assertEqual(str(logical),
                         "((((~(?) & True) | False) -> 'a') <-> 'b')")
        self.assertEqual(str(unary),
                         "AX (EX (AG (EG (AF (EF (?))))))")
        self.assertEqual(str(binary),
                         "A[True U A[True W E[True U E[True W ?]]]]")
        self.assertEqual(str(binary2),
                         "A[True oU A[True oW E[True oU E[True oW ?]]]]")
        self.assertEqual(str(binary3),
                         "A[True dU A[True dW E[True dU E[True dW ?]]]]")

    def test_not(self):
        ast = parse_ctlq("~?")

        self.assertEqual(type(ast), Not)
        self.assertEqual(type(ast.child), Placeholder)

    def test_and(self):
        ast = parse_ctlq("? & True")

        self.assertEqual(type(ast), And)
        self.assertEqual(type(ast.left), Placeholder)
        self.assertEqual(type(ast.right), TrueExp)

    def test_or(self):
        ast = parse_ctlq("False | ?")

        self.assertEqual(type(ast), Or)
        self.assertEqual(type(ast.left), FalseExp)
        self.assertEqual(type(ast.right), Placeholder)

    def test_imply(self):
        ast = parse_ctlq("? -> 'a = 42'")

        self.assertEqual(type(ast), Imply)
        self.assertEqual(type(ast.left), Placeholder)
        self.assertEqual(type(ast.right), Atom)
        self.assertEqual(ast.right.value, 'a = 42')

    def test_iff(self):
        ast = parse_ctlq("'a = 42' <-> ?")

        self.assertEqual(type(ast), Iff)
        self.assertEqual(type(ast.left), Atom)
        self.assertEqual(ast.left.value, 'a = 42')
        self.assertEqual(type(ast.right), Placeholder)

    def test_ax(self):
        ast = parse_ctlq("AX ?")

        self.assertEqual(type(ast), AX)
        self.assertEqual(type(ast.child), Placeholder)

    def test_af(self):
        ast = parse_ctlq("AF ?")

        self.assertEqual(type(ast), AF)
        self.assertEqual(type(ast.child), Placeholder)

    def test_ag(self):
        ast = parse_ctlq("AG ?")

        self.assertEqual(type(ast), AG)
        self.assertEqual(type(ast.child), Placeholder)

    def test_au(self):
        ast = parse_ctlq("A[? U 'a']")

        self.assertEqual(type(ast), AU)
        self.assertEqual(type(ast.left), Placeholder)
        self.assertEqual(type(ast.right), Atom)
        self.assertEqual(ast.right.value, 'a')

    def test_aw(self):
        ast = parse_ctlq("A['a' W ?]")

        self.assertEqual(type(ast), AW)
        self.assertEqual(type(ast.left), Atom)
        self.assertEqual(ast.left.value, 'a')
        self.assertEqual(type(ast.right), Placeholder)

    def test_ex(self):
        ast = parse_ctlq("EX ?")

        self.assertEqual(type(ast), EX)
        self.assertEqual(type(ast.child), Placeholder)

    def test_ef(self):
        ast = parse_ctlq("EF ?")

        self.assertEqual(type(ast), EF)
        self.assertEqual(type(ast.child), Placeholder)

    def test_eg(self):
        ast = parse_ctlq("EG ?")

        self.assertEqual(type(ast), EG)
        self.assertEqual(type(ast.child), Placeholder)

    def test_eu(self):
        ast = parse_ctlq("E[? U 'a']")

        self.assertEqual(type(ast), EU)
        self.assertEqual(type(ast.left), Placeholder)
        self.assertEqual(type(ast.right), Atom)
        self.assertEqual(ast.right.value, 'a')

    def test_ew(self):
        ast = parse_ctlq("E['a' W ?]")

        self.assertEqual(type(ast), EW)
        self.assertEqual(type(ast.left), Atom)
        self.assertEqual(ast.left.value, 'a')
        self.assertEqual(type(ast.right), Placeholder)

    def test_aou(self):
        ast = parse_ctlq("A[? oU 'a']")

        self.assertEqual(type(ast), AoU)
        self.assertEqual(type(ast.left), Placeholder)
        self.assertEqual(type(ast.right), Atom)
        self.assertEqual(ast.right.value, 'a')

    def test_aow(self):
        ast = parse_ctlq("A['a' oW ?]")

        self.assertEqual(type(ast), AoW)
        self.assertEqual(type(ast.left), Atom)
        self.assertEqual(ast.left.value, 'a')
        self.assertEqual(type(ast.right), Placeholder)

    def test_adu(self):
        ast = parse_ctlq("A[? dU 'a']")

        self.assertEqual(type(ast), AdU)
        self.assertEqual(type(ast.left), Placeholder)
        self.assertEqual(type(ast.right), Atom)
        self.assertEqual(ast.right.value, 'a')

    def test_adw(self):
        ast = parse_ctlq("A['a' dW ?]")

        self.assertEqual(type(ast), AdW)
        self.assertEqual(type(ast.left), Atom)
        self.assertEqual(ast.left.value, 'a')
        self.assertEqual(type(ast.right), Placeholder)

    def test_eou(self):
        ast = parse_ctlq("E[? oU 'a']")

        self.assertEqual(type(ast), EoU)
        self.assertEqual(type(ast.left), Placeholder)
        self.assertEqual(type(ast.right), Atom)
        self.assertEqual(ast.right.value, 'a')

    def test_eow(self):
        ast = parse_ctlq("E['a' oW ?]")

        self.assertEqual(type(ast), EoW)
        self.assertEqual(type(ast.left), Atom)
        self.assertEqual(ast.left.value, 'a')
        self.assertEqual(type(ast.right), Placeholder)

    def test_edu(self):
        ast = parse_ctlq("E[? dU 'a']")

        self.assertEqual(type(ast), EdU)
        self.assertEqual(type(ast.left), Placeholder)
        self.assertEqual(type(ast.right), Atom)
        self.assertEqual(ast.right.value, 'a')

    def test_edw(self):
        ast = parse_ctlq("E['a' dW ?]")

        self.assertEqual(type(ast), EdW)
        self.assertEqual(type(ast.left), Atom)
        self.assertEqual(ast.left.value, 'a')
        self.assertEqual(type(ast.right), Placeholder)

    def test_not_equal(self):
        list1 = ["?",
                 "AX ?",
                 "AF ?",
                 "EG (True & ?)",
                 "E[? U True]",
                 "A[False W ?]",
                 "A['a' W ?]",
                 "A['a' oU ?]"]
        list2 = ["~?",
                 "EX ?",
                 "AF ~?",
                 "EG (False & ?)",
                 "A[? U True]",
                 "A[False U ?]",
                 "A[? W 'a']",
                 "A['b' oU ?]"]

        for (elem1, elem2) in zip(list1, list2):
            self.assertNotEqual(parse_ctlq(elem1), parse_ctlq(elem2))

    def test_parentheses(self):
        list1 = ["?",
                 "'a' & 'b' | ?",
                 "A['a' U ?]",
                 "~ EF ?"]
        list2 = ["((((?))))",
                 "(('a') & ('b')) | (?)",
                 "(A[(('a')) U (?)])",
                 "((~EF ((?))))"]

        for (elem1, elem2) in zip(list1, list2):
            self.assertEqual(parse_ctlq(elem1), parse_ctlq(elem2))

    def test_commutativity(self):
        list1 = ["?",
                 "? & 'a'",
                 "? | 'a'",
                 "? <-> 'a'",
                 "? | 'a' & ~True"]
        list2 = ["?",
                 "'a' & ?",
                 "'a' | ?",
                 "'a' <-> ?",
                 "~True & 'a' | ?"]

        for (elem1, elem2) in zip(list1, list2):
            self.assertEqual(parse_ctlq(elem1), parse_ctlq(elem2))

    def test_associativity(self):
        list1 = ["'a' & 'b' & ?",
                 "'a' | 'b' | ?",
                 "'a' <-> 'b' <-> ?",
                 "'a' -> 'b' -> ?"]
        list2 = ["('a' & 'b') & ?",
                 "('a' | 'b') | ?",
                 "('a' <-> 'b') <-> ?",
                 "'a' -> ('b' -> ?)"]

        for (elem1, elem2) in zip(list1, list2):
            self.assertEqual(parse_ctlq(elem1), parse_ctlq(elem2))

    def test_precedence(self):
        list1 = ["? | 'a' & ~True",
                 "'a' & 'b' -> ~'c' | ?",
                 "AG ~? | 'a'",
                 "AF ~(? & 'a') & 'b'",
                 "AX ~AG 'a' & ? | 'b'",
                 "E[~'a' & ? dW ~AX 'b']",
                 "EX AX 'a' & EX AX ?"]
        list2 = ["((?) | (('a') & (~(True))))",
                 "((('a') & ('b')) -> ((~('c')) | (?)))",
                 "((AG (~(?))) | ('a'))",
                 "((AF ~((?) & ('a'))) & ('b'))",
                 "(((AX (~(AG ('a')))) & (?)) | ('b'))",
                 "(E[((~('a')) & (?)) dW (~(AX ('b')))])",
                 "((EX (AX ('a'))) & (EX (AX (?))))"]

        for (elem1, elem2) in zip(list1, list2):
            self.assertEqual(parse_ctlq(elem1), parse_ctlq(elem2))

    def test_fail_parsing(self):
        kos = ["",
               "'test",
               "AG true",
               "EX ? True",
               "A(? U 'a')",
               "A[& U ~]",
               "(EF ?",
               "'a' (&) ?",
               "E['a' (U) ?]",
               "E AF [? oW False]"]

        for ko in kos:
            with self.assertRaises(pyparsing.ParseException):
                parse_ctlq(ko)

    def test_fail_no_placeholder(self):
        kos = ["False",
               "~'a'",
               "EF True",
               "'a = 3' & 'b = 2'",
               "A['b' U 'a']"]

        for ko in kos:
            with self.assertRaises(NoPlaceholderError):
                parse_ctlq(ko)
